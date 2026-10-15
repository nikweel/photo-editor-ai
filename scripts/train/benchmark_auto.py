"""Бенчмарк автоэкспозиции на отложенных кадрах (не участвовали в обучении): синтетические сдвиги ±2 EV, ошибка поправки по типам сцен.

Исходный кадр считается «правильным», сдвиг имитирует недо/переэкспозицию, правильный ответ — вернуть сдвиг назад.
Сравниваются: гистограммная эвристика, IAT-exposure (как работает приложение), новая модель с учётом сцены.
Запуск: python scripts/train/benchmark_auto.py [--head data/train/exposure_scene.onnx]
"""
import argparse
from collections import defaultdict

import numpy as np

from common import images, is_test, load, session

from app.ai import exposure
from app.ai.registry import Engine, is_available
from app.ai.scene import features, shift_exposure

SHIFTS = (-2.0, -1.0, 0.0, 1.0, 2.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--head", default="data/train/exposure_scene.onnx")
    a = ap.parse_args()
    import onnxruntime as ort

    emb = session()
    head = ort.InferenceSession(open(a.head, "rb").read(), providers=["CPUExecutionProvider"])
    methods = {"гистограмма": lambda im, f: exposure.heuristic_ev(im), "новая модель": lambda im, f: float(head.run(None, {"features": f[None]})[0].ravel()[0])}
    if is_available("iat_exposure"):
        from app.ai.auto import suggest

        eng = Engine("iat_exposure")
        methods["IAT (как в приложении)"] = lambda im, f: suggest(eng, im, "exposure")["exposure"]
    err = {m: defaultdict(list) for m in methods}
    test = [(n, c) for n, c in images() if is_test(n)]
    print(f"отложенных кадров: {len(test)}, сдвигов на кадр: {len(SHIFTS)}")
    for n, cls in test:
        img = load(n)
        for s in SHIFTS:
            sh = shift_exposure(img, s)
            f = features(emb, sh)
            for m, fn in methods.items():
                e = abs(float(np.clip(fn(sh, f), -3, 3)) - (-s))
                err[m][cls].append(e)
                err[m]["ВСЕ"].append(e)
                err[m][f"сдвиг {s:+.0f}"].append(e)
    cols = list(methods)
    print(f"{'группа':14}" + "".join(f"{m:>26}" for m in cols))
    for g in sorted(err[cols[0]], key=lambda k: (k.startswith("сдвиг"), k == "ВСЕ", k)):
        print(f"{g:14}" + "".join(f"{np.mean(err[m][g]):>20.2f} EV   " for m in cols), f"(n={len(err[cols[0]][g])})")


if __name__ == "__main__":
    main()
