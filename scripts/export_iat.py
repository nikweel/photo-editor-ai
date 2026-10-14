"""Экспорт весов IAT (Illumination-Adaptive Transformer, Apache-2.0) в ONNX.
Запуск (нужны torch и timm==0.9.*, они только для экспорта и в приложение не входят):
  python scripts/export_iat.py <папка с model/ и *.pth из репозитория cuiziteng/Illumination-Adaptive-Transformer/IAT_enhance> <куда>
Веса читаются с weights_only=True: pickle-код из файла не исполняется."""
import sys
import types
from pathlib import Path

import numpy as np
import torch

src, out = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(src))
sys.modules.setdefault("imp", types.ModuleType("imp"))  # в коде репозитория лишний `import imp`, которого нет в Python 3.12
from model.IAT_main import IAT  # noqa: E402

JOBS = {"iat_exposure.onnx": ("best_Epoch_exposure.pth", "exp"), "iat_lowlight.onnx": ("best_Epoch_lol_v1.pth", "lol")}


class Export(torch.nn.Module):
    """Тот же расчёт, что IAT.forward, но без Python-цикла по батчу и tensordot с отрицательными осями."""

    def __init__(self, net):
        super().__init__()
        self.net = net

    def forward(self, x):
        mul, add = self.net.local_net(x)
        high = x * mul + add
        gamma, color = self.net.global_net(x)
        h = high.permute(0, 2, 3, 1)
        h = torch.clamp(torch.matmul(h, color.transpose(1, 2).unsqueeze(1)), 1e-8, 1.0)
        return (h ** gamma.view(-1, 1, 1, 1)).permute(0, 3, 1, 2)


for name, (ckpt, typ) in JOBS.items():
    net = IAT(type=typ)
    net.load_state_dict(torch.load(src / ckpt, map_location="cpu", weights_only=True))
    net.eval()
    wrap = Export(net).eval()
    x = torch.rand(1, 3, 192, 256)
    with torch.no_grad():
        ref_orig = net(x)[2]
        ref = wrap(x)
    assert torch.allclose(ref, ref_orig, atol=1e-5), "обёртка расходится с оригиналом"
    out.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(wrap, x, str(out / name), input_names=["input"], output_names=["output"], opset_version=17,
                      dynamic_axes={"input": {2: "h", 3: "w"}, "output": {2: "h", 3: "w"}}, dynamo=False)
    print(name, "ok", (out / name).stat().st_size, "bytes")
