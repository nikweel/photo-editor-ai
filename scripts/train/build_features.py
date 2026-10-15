"""Считает признаки (DINOv2 + статистика яркости) для кадров с синтетическими сдвигами экспозиции -> data/train/features.npz."""
import time

import numpy as np

from common import ROOT, images, is_test, load, session, shifts

from app.ai.scene import CLASSES, features, shift_exposure


def main():
    sess = session()
    rng = np.random.default_rng(11)
    X, Y, C, S, T, N = [], [], [], [], [], []
    items = images()
    t0 = time.time()
    for i, (name, cls) in enumerate(items):
        try:
            img = load(name)
        except Exception as e:
            print("пропуск", name, e)
            continue
        for ev in shifts(rng):
            X.append(features(sess, shift_exposure(img, float(ev))))
            Y.append(-ev)  # нужная поправка = обратный сдвиг
            C.append(CLASSES.index(cls))
            S.append(i)
            T.append(is_test(name))
            N.append(name)
        if i % 50 == 0:
            print(f"{i}/{len(items)} {time.time() - t0:.0f}s", flush=True)
    np.savez_compressed(ROOT / "data" / "train" / "features.npz", X=np.array(X, np.float32), y=np.array(Y, np.float32), c=np.array(C), img=np.array(S), test=np.array(T), name=np.array(N))
    print("готово:", len(X), "примеров")


if __name__ == "__main__":
    main()
