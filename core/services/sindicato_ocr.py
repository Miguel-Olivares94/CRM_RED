"""
Servicio OCR para SindiApp.

Patrón adaptador: OCRProviderBase define la interfaz; los proveedores concretos
implementan extract_text().  extract_data() opera sobre texto plano y es
independiente del proveedor (pura lógica regex).

Proveedores disponibles:
  - PytesseractProvider  → pytesseract + Pillow/pdf2image (instalación local)
  - DemoOCRProvider      → fallback controlado para entornos sin OCR instalado
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Resultado de extracción
# ---------------------------------------------------------------------------

@dataclass
class DatosExtraidos:
    rut: str = ""
    nombre: str = ""
    tipo_documento: str = ""
    numero_documento: str = ""
    fecha: str = ""
    monto_neto: str = ""
    iva: str = ""
    total: str = ""
    beneficio_sugerido: str = ""
    observaciones: str = ""
    confianza: str = "BAJA"   # ALTA / MEDIA / BAJA

    def to_dict(self) -> dict:
        return {
            "rut": self.rut,
            "nombre": self.nombre,
            "tipo_documento": self.tipo_documento,
            "numero_documento": self.numero_documento,
            "fecha": self.fecha,
            "monto_neto": self.monto_neto,
            "iva": self.iva,
            "total": self.total,
            "beneficio_sugerido": self.beneficio_sugerido,
            "observaciones": self.observaciones,
            "confianza": self.confianza,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "DatosExtraidos":
        return cls(**{k: d.get(k, "") for k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# Base abstracta del adaptador
# ---------------------------------------------------------------------------

class OCRProviderBase(ABC):
    """Contrato mínimo para cualquier proveedor OCR."""

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Devuelve el texto crudo extraído del archivo."""

    def nombre_proveedor(self) -> str:
        return self.__class__.__name__

    # extract_data es compartido — opera sobre texto ya extraído
    def extract_data(self, text: str) -> DatosExtraidos:
        return _parse_texto(text)


# ---------------------------------------------------------------------------
# Proveedor: pytesseract + Pillow / pdf2image
# ---------------------------------------------------------------------------

class PytesseractProvider(OCRProviderBase):

    def extract_text(self, file_path: str) -> str:
        import pytesseract
        from PIL import Image

        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            pages = self._pdf_to_images(file_path)
            return "\n\n".join(
                pytesseract.image_to_string(p, lang="spa") for p in pages
            )

        img = Image.open(file_path)
        return pytesseract.image_to_string(img, lang="spa")

    @staticmethod
    def _pdf_to_images(file_path: str):
        try:
            from pdf2image import convert_from_path
            return convert_from_path(file_path, dpi=200)
        except Exception:
            pass
        try:
            import fitz
            from PIL import Image
            import io
            doc = fitz.open(file_path)
            images = []
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                images.append(Image.open(io.BytesIO(pix.tobytes("png"))))
            return images
        except Exception:
            return []


# ---------------------------------------------------------------------------
# Proveedor: Pillow sin OCR (modo imagen → texto vacío, datos demo)
# ---------------------------------------------------------------------------

class PillowDemoProvider(OCRProviderBase):
    """
    Usa Pillow para verificar que el archivo es válido pero devuelve
    texto simulado.  Activo cuando pytesseract no está instalado.
    """

    def extract_text(self, file_path: str) -> str:
        from PIL import Image
        path = Path(file_path)
        suffix = path.suffix.lower()
        if suffix != ".pdf":
            try:
                Image.open(file_path).verify()
            except Exception as exc:
                raise ValueError(f"Archivo de imagen inválido: {exc}") from exc
        return _demo_texto()

    def nombre_proveedor(self) -> str:
        return "PillowDemo"


# ---------------------------------------------------------------------------
# Proveedor: demo puro (sin dependencias)
# ---------------------------------------------------------------------------

class DemoOCRProvider(OCRProviderBase):
    """
    Fallback controlado: no requiere ninguna dependencia extra.
    Devuelve datos de ejemplo para permitir pruebas de flujo completo.
    """

    def extract_text(self, _file_path: str) -> str:
        return _demo_texto()

    def nombre_proveedor(self) -> str:
        return "Demo"


# ---------------------------------------------------------------------------
# Fábrica de proveedores
# ---------------------------------------------------------------------------

def get_ocr_provider() -> OCRProviderBase:
    """
    Retorna el mejor proveedor disponible en el entorno actual.
    Orden de preferencia: pytesseract → Pillow demo → demo puro.
    """
    try:
        import pytesseract  # noqa: F401
        from PIL import Image  # noqa: F401
        return PytesseractProvider()
    except ImportError:
        pass

    try:
        from PIL import Image  # noqa: F401
        return PillowDemoProvider()
    except ImportError:
        pass

    return DemoOCRProvider()


# ---------------------------------------------------------------------------
# Parseo de texto con regex (independiente del proveedor)
# ---------------------------------------------------------------------------

_RUT_RE = re.compile(
    r"\b(\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]|\d{7,8}-[\dkK])\b"
)
_MONTO_RE = re.compile(
    r"(?:total|neto|monto|precio|valor|iva)\s*[:\-]?\s*\$?\s*([\d\.,]+)",
    re.IGNORECASE,
)
_IVA_RE = re.compile(
    r"iva\s*[:\-]?\s*\$?\s*([\d\.,]+)",
    re.IGNORECASE,
)
_FECHA_RE = re.compile(
    r"\b(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{4}[/\-]\d{2}[/\-]\d{2})\b"
)
_NDOC_RE = re.compile(
    r"(?:factura|boleta|n[°º.]?\s*doc(?:umento)?|folio)\s*(?:n[°º\.]\s*)?[:\-]?\s*(\d+)",
    re.IGNORECASE,
)
_TIPO_DOC_RE = re.compile(
    r"\b(factura|boleta|nota de crédito|nota de debito|liquidación)\b",
    re.IGNORECASE,
)

_BENEFICIO_KEYWORDS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bgas\b", re.IGNORECASE), "Gas"),
    (re.compile(r"\btelefo|celular|m[oó]vil", re.IGNORECASE), "Telefonía"),
    (re.compile(r"\bcopeuch|cooperativa", re.IGNORECASE), "Copeuch"),
    (re.compile(r"\bsalud|cl[ií]nica|m[eé]dico|isapre", re.IGNORECASE), "Salud"),
    (re.compile(r"\beducac|colegio|instituto|universidad", re.IGNORECASE), "Educación"),
    (re.compile(r"\bsupermercado|alimento|víveres", re.IGNORECASE), "Alimentación"),
]


def _parse_texto(text: str) -> DatosExtraidos:
    datos = DatosExtraidos()

    rut_m = _RUT_RE.search(text)
    if rut_m:
        datos.rut = rut_m.group(1)

    tipo_m = _TIPO_DOC_RE.search(text)
    if tipo_m:
        datos.tipo_documento = tipo_m.group(1).capitalize()

    ndoc_m = _NDOC_RE.search(text)
    if ndoc_m:
        datos.numero_documento = ndoc_m.group(1)

    fecha_m = _FECHA_RE.search(text)
    if fecha_m:
        datos.fecha = fecha_m.group(1)

    iva_m = _IVA_RE.search(text)
    if iva_m:
        datos.iva = iva_m.group(1).replace(".", "").replace(",", "")

    montos = _MONTO_RE.findall(text)
    if montos:
        numeros = [m.replace(".", "").replace(",", "") for m in montos]
        numeros_int = []
        for n in numeros:
            try:
                numeros_int.append(int(n))
            except ValueError:
                pass
        if numeros_int:
            datos.total = str(max(numeros_int))
            if datos.iva:
                try:
                    datos.monto_neto = str(max(numeros_int) - int(datos.iva))
                except ValueError:
                    datos.monto_neto = datos.total
            else:
                datos.monto_neto = datos.total

    for pattern, beneficio in _BENEFICIO_KEYWORDS:
        if pattern.search(text):
            datos.beneficio_sugerido = beneficio
            break

    campos_detectados = sum(
        bool(v) for v in [
            datos.rut, datos.tipo_documento, datos.fecha,
            datos.total, datos.beneficio_sugerido,
        ]
    )
    if campos_detectados >= 4:
        datos.confianza = "ALTA"
    elif campos_detectados >= 2:
        datos.confianza = "MEDIA"

    return datos


def _demo_texto() -> str:
    return (
        "[MODO DEMO — OCR no instalado]\n\n"
        "RUT: 12.345.678-9\n"
        "Nombre: Empresa Ejemplo S.A.\n"
        "Factura N° 001234\n"
        "Fecha: 15/06/2026\n"
        "Gas Licuado — Distribución\n"
        "Neto: $84.034\n"
        "IVA: $15.966\n"
        "Total: $100.000\n"
    )


# ---------------------------------------------------------------------------
# Función principal de procesamiento
# ---------------------------------------------------------------------------

def procesar_documento(file_path: str) -> tuple[str, DatosExtraidos]:
    """
    Extrae texto y datos de un archivo.
    Devuelve (texto_extraido, DatosExtraidos).
    Propaga cualquier excepción para que la vista la capture y registre ERROR.
    """
    provider = get_ocr_provider()
    texto = provider.extract_text(file_path)
    datos = provider.extract_data(texto)
    return texto, datos
