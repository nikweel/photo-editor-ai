"""Обучает «голову» (MLP на numpy) по data/train/features.npz и сравнивает варианты на отложенных кадрах; экспорт в ONNX.

Варианты: только статистика яркости / эмбеддинг + статистика. Качество — средняя ошибка поправки в EV на тестовых кадрах.
Запуск: python train_head.py [--export models/exposure_scene.onnx]
"""
import argparse

import numpy as np

from common import ROOT

from app.ai.scene import CLASSES, EMB_DIM, STAT_DIM


def mlp_train(X, y, c, hidden=(128, 64), epochs=60, lr=2e-3, wd=1e-4, cls_w=0.3, seed=0):
    rng = np.random.default_rng(seed)
    sizes = [X.shape[1], *hidden]
    W = [rng.normal(0, np.sqrt(2 / a), (a, b)).astype(np.float32) for a, b in zip(sizes[:-1], sizes[1:])]
    B = [np.zeros(b, np.float32) for b in sizes[1:]]
    Wo = rng.normal(0, 0.05, (sizes[-1], 1 + len(CLASSES))).astype(np.float32)
    Bo = np.zeros(1 + len(CLASSES), np.float32)
    params = [*W, *B, Wo, Bo]
    m = [np.zeros_like(p) for p in params]
    v = [np.zeros_like(p) for p in params]
    n, t = len(X), 0
    onehot = np.eye(len(CLASSES), dtype=np.float32)[c]
    for ep in range(epochs):
        cur = lr * 0.5 * (1 + np.cos(np.pi * ep / epochs))
        perm = rng.permutation(n)
        for i in range(0, n, 128):
            idx = perm[i : i + 128]
            xb = X[idx]
            xb = xb + rng.normal(0, 0.05, xb.shape).astype(np.float32)  # лёгкий шум против переобучения на 1800 кадрах
            hs = [xb]
            for w, b in zip(W, B):
                hs.append(np.maximum(hs[-1] @ w + b, 0))
            out = hs[-1] @ Wo + Bo
            err = out[:, 0] - y[idx]
            g_ev = np.clip(err, -0.5, 0.5) / len(idx)  # Huber (δ=0.5 EV)
            z = out[:, 1:] - out[:, 1:].max(1, keepdims=True)
            p = np.exp(z) / np.exp(z).sum(1, keepdims=True)
            g = np.concatenate([g_ev[:, None], cls_w * (p - onehot[idx]) / len(idx)], 1)
            gWo, gBo = hs[-1].T @ g, g.sum(0)
            gh = g @ Wo.T
            grads_W, grads_B = [], []
            for k in range(len(W) - 1, -1, -1):
                gh = gh * (hs[k + 1] > 0)
                grads_W.insert(0, hs[k].T @ gh + wd * W[k])
                grads_B.insert(0, gh.sum(0))
                gh = gh @ W[k].T
            grads = [*grads_W, *grads_B, gWo, gBo]
            t += 1
            for j, (p_, g_) in enumerate(zip(params, grads)):
                m[j] = 0.9 * m[j] + 0.1 * g_
                v[j] = 0.999 * v[j] + 0.001 * g_ * g_
                p_ -= cur * (m[j] / (1 - 0.9**t)) / (np.sqrt(v[j] / (1 - 0.999**t)) + 1e-8)
    return W, B, Wo, Bo


def mlp_predict(model, X):
    W, B, Wo, Bo = model
    h = X
    for w, b in zip(W, B):
        h = np.maximum(h @ w + b, 0)
    out = h @ Wo + Bo
    return out[:, 0], out[:, 1:]


def export_onnx(model, mean, std, proj, path):
    """Сводит PCA эмбеддинга и нормализацию в первый слой: модель принимает сырой вектор признаков [1, 406]."""
    import onnx
    from onnx import TensorProto, helper, numpy_helper as nh

    W, B, Wo, Bo = model
    pmu, V = proj  # V: [EMB_DIM, k]
    k = V.shape[1]
    A = np.zeros((EMB_DIM + STAT_DIM, k + STAT_DIM), np.float32)
    A[:EMB_DIM, :k] = V
    A[EMB_DIM:, k:] = np.eye(STAT_DIM)
    c0 = np.concatenate([-pmu @ V, np.zeros(STAT_DIM, np.float32)])
    W0 = (A / std) @ W[0]
    B0 = ((c0 - mean) / std) @ W[0] + B[0]
    Ws, Bs = [W0.astype(np.float32), *W[1:]], [B0.astype(np.float32), *B[1:]]
    init, nodes = [], []
    for i, (w, b) in enumerate(zip(Ws, Bs)):
        init += [nh.from_array(w, f"w{i}"), nh.from_array(b, f"b{i}")]
        src = "features" if i == 0 else f"h{i}"
        nodes += [helper.make_node("MatMul", [src, f"w{i}"], [f"m{i}"]), helper.make_node("Add", [f"m{i}", f"b{i}"], [f"a{i}"]), helper.make_node("Relu", [f"a{i}"], [f"h{i + 1}"])]
    n = 1 + len(CLASSES)
    init += [nh.from_array(Wo, "wo"), nh.from_array(Bo, "bo")] + [nh.from_array(np.array([v], np.int64), nm) for nm, v in (("s0", 0), ("s1", 1), ("sn", n), ("ax", 1))]
    nodes += [helper.make_node("MatMul", [f"h{len(Ws)}", "wo"], ["mo"]), helper.make_node("Add", ["mo", "bo"], ["out"]),
              helper.make_node("Slice", ["out", "s0", "s1", "ax"], ["ev"]), helper.make_node("Slice", ["out", "s1", "sn", "ax"], ["scene"])]
    g = helper.make_graph(nodes, "exposure_scene", [helper.make_tensor_value_info("features", TensorProto.FLOAT, [1, EMB_DIM + STAT_DIM])],
                          [helper.make_tensor_value_info("ev", TensorProto.FLOAT, [1, 1]), helper.make_tensor_value_info("scene", TensorProto.FLOAT, [1, len(CLASSES)])], init)
    m = helper.make_model(g, opset_imports=[helper.make_opsetid("", 13)])
    m.ir_version = 8
    onnx.checker.check_model(m)
    onnx.save(m, path)


def fit(X, y, c, tr, k=8, wd=1e-2, epochs=40):
    """PCA(эмбеддинг, k) + статистика -> нормализация -> MLP. Возвращает (модель, mean, std, (pmu, V))."""
    emb, st = X[:, :EMB_DIM], X[:, EMB_DIM:]
    pmu = emb[tr].mean(0)
    V = np.linalg.svd(emb[tr] - pmu, full_matrices=False)[2][:k].T.astype(np.float32)
    F = np.concatenate([(emb - pmu) @ V, st], 1)
    mean, std = F[tr].mean(0), F[tr].std(0) + 1e-6
    Z = ((F - mean) / std).astype(np.float32)
    return mlp_train(Z[tr], y[tr], c[tr], wd=wd, epochs=epochs), mean, std, (pmu, V), Z


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export")
    a = ap.parse_args()
    d = np.load(ROOT / "data" / "train" / "features.npz")
    X, y, c, test = d["X"], d["y"], d["c"], d["test"]
    tr, te = ~test, test
    print(f"обучение {tr.sum()} примеров, тест {te.sum()} (кадры в тесте в обучении не участвовали)")
    model, mean, std, proj, Z = fit(X, y, c, tr)
    ev, logits = mlp_predict(model, Z[te])
    mae = np.abs(ev - y[te])
    print(f"PCA8 + яркость: MAE {mae.mean():.3f} EV, медиана {np.median(mae):.3f}, класс сцены {(logits.argmax(1) == c[te]).mean():.0%}")
    if a.export:
        export_onnx(model, mean, std, proj, a.export)
        print("экспорт:", a.export)


if __name__ == "__main__":
    main()
