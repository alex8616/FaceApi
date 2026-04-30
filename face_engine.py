import numpy as np
from insightface.app import FaceAnalysis

class FaceEngine:

    def __init__(self):
        self.app = FaceAnalysis(name='buffalo_l')
        self.app.prepare(ctx_id=0, det_size=(320, 320))  # ⚡ rápido

    def get_embedding(self, frame):
        faces = self.app.get(frame)

        if len(faces) == 0:
            return None

        emb = faces[0].embedding

        # 🔥 NORMALIZACIÓN (ESTO ES LO QUE TE FALTA)
        emb = emb / np.linalg.norm(emb)

        return emb

    def compare(self, emb1, emb2):
        return np.linalg.norm(emb1 - emb2)