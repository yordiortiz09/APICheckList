from fpdf import FPDF
from datetime import datetime
from io import BytesIO
from datetime import datetime, time
import locale
class PDF(FPDF):

    def __init__(self, orden_servicio="", folio_fisico="", sucursal="", recolector="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orden_servicio = orden_servicio or ""
        self.folio_fisico = folio_fisico or ""
        self.sucursal = sucursal or ""
        self.recolector = recolector or ""
        self.unifontsubset = False

    def header(self):
        self.set_font("Arial", "B", 10)
        self.image("app/src/HuellitasLogo.jpg", x=10, y=8, w=50)

        self.set_xy(160, 10)
        self.set_fill_color(200, 200, 200)
        self.cell(40, 6, "ORDEN DE SERVICIO", border=1, ln=2, align="C", fill=True)

        self.set_text_color(255, 0, 0)
        self.cell(40, 6, str(self.orden_servicio), border=1, ln=2, align="C")
        self.set_text_color(0, 0, 0)

        self.set_fill_color(200, 200, 200)
        self.cell(40, 6, "FOLIO FISICO", border=1, ln=2, align="C", fill=True)

        self.set_text_color(255, 0, 0)
        self.cell(40, 6, str(self.folio_fisico), border=1, ln=2, align="C")
        self.set_text_color(0, 0, 0)

        self.set_font("Arial", "", 9)

        fecha_str = self.formatear_fecha(getattr(self, 'fecha_pedido', None))
        hora_str = self.formatear_hora(getattr(self, 'hora_pedido', None))

        self.cell(40, 6, f"Fecha: {fecha_str}", ln=2, align="R")
        self.cell(40, 6, f"Hora: {hora_str}", ln=2, align="R")
        self.cell(40, 6, f"Sucursal: {self.sucursal}", ln=2, align="R")

        self.ln(5)

    def formatear_fecha(self, fecha):
        if isinstance(fecha, str):
            try:
                fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
                return fecha_dt.strftime('%d/%m/%Y')
            except ValueError:
                return fecha
        elif isinstance(fecha, datetime):
            return fecha.strftime('%d/%m/%Y')
        return datetime.now().strftime('%d/%m/%Y')

    def formatear_hora(self, hora):
        if isinstance(hora, time):
            return hora.strftime('%I:%M:%S %p').lower().replace('am', 'a. m.').replace('pm', 'p. m.')
        elif isinstance(hora, str):
            return hora
        return datetime.now().strftime('%I:%M:%S %p').lower().replace('am', 'a. m.').replace('pm', 'p. m.')

    def add_labeled_line(self, label, value="", line_height=7):
        value = str(value or "")
        self.set_font("Arial", "B", 9)
        self.cell(55, line_height, label, 1)
        self.set_font("Arial", "", 9)
        self.cell(135, line_height, value, 1, ln=True)

    def add_half_line(self, label1, val1, label2, val2, w1=25, w2=50, w3=35, w4=45):
        self.cell(w1, 7, label1, 1)
        self.cell(w2, 7, str(val1 or ""), 1)
        self.cell(w3, 7, label2, 1)
        self.cell(w4, 7, str(val2 or ""), 1, ln=True)

    def footer(self):
        self.set_y(-30)
        self.set_font("Arial", "", 9)
        self.cell(0, 6, "_____________________________", ln=True, align="C")
        self.cell(0, 6, str(self.recolector).upper(), ln=True, align="C")
        self.cell(0, 6, "RECOLECTOR", ln=True, align="C")


def generar_pdf(datos: dict, articulos: list, campos: dict, clave_pedido: str, referencia_pedido: str, fecha: str, hora: str, sucursal: str, recolector: str) -> bytes:
    pdf = PDF(orden_servicio=clave_pedido, folio_fisico=referencia_pedido, sucursal=sucursal, recolector=recolector)
    pdf.fecha_pedido = fecha
    pdf.hora_pedido = hora
    pdf.sucursal = sucursal

    pdf.add_page()

    def safe_str(valor):
        return str(valor or "")

    pdf.add_labeled_line("NOMBRE DE LA MASCOTA:", datos.get("NOMBRE DE LA MASCOTA"))
    pdf.set_font("Arial", "B", 9)
    pdf.cell(85, 7, "VETERINARIO QUE LA ATIENDE REGULARMENTE:", 1)
    pdf.set_font("Arial", "", 9)
    pdf.cell(105, 7, datos.get("VETERINARIO"), 1, ln=True)

    pdf.set_font("Arial", "B", 9)
    pdf.cell(25, 7, "RAZA:", 1)
    pdf.set_font("Arial", "", 9)
    pdf.cell(60, 7, datos.get("RAZA"), 1)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(25, 7, "PESO:", 1)
    pdf.set_font("Arial", "", 9)
    pdf.cell(80, 7, datos.get("PESO"), 1, ln=True)

    pdf.set_font("Arial", "B", 9)
    pdf.cell(25, 7, "EDAD:", 1)
    pdf.set_font("Arial", "", 9)
    pdf.cell(35, 7, datos.get("EDAD"), 1)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(40, 7, "CAUSA DE MUERTE:", 1)
    pdf.set_font("Arial", "", 9)
    pdf.cell(90, 7, datos.get("CAUSA DE MUERTE"), 1, ln=True)

    pdf.add_labeled_line("DUEÑO O CONTRATANTE:", datos.get("DUEÑO O CONTRATANTE"))
    pdf.add_labeled_line("DOMICILIO:", datos.get("DOMICILIO"))
    pdf.add_labeled_line("TELEFONO(S):", datos.get("TELEFONO(S)"))
    pdf.add_labeled_line("¿CÓMO SUPO DE NOSOTROS?", datos.get("¿CÓMO SUPO DE NOSOTROS?"))
    pdf.add_labeled_line("LUGAR DE RECOLECCION:", datos.get("LUGAR DE RECOLECCION"))

    y_inicio = pdf.get_y()
    pdf.set_xy(10, y_inicio)
    pdf.set_font("Arial", "B", 9)
    pdf.multi_cell(65, 5, "ESPECIFICACIONES DEL SERVICIO:\n(Certificación, lugar y fecha de entrega\nde cenizas, hora de cremación,\nobituario personalizado)", border=1)
    pdf.set_xy(75, y_inicio)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(125, 20, datos.get("ESPECIFICACIONES"), border=1)
    pdf.set_y(y_inicio + 20)

    pdf.add_labeled_line("DUEÑO, DUEÑA O FAMILIA:", datos.get("FAMILIA"))

    # Detalle de productos/servicios
    pdf.ln(2)
    pdf.set_fill_color(200, 200, 200)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 8, "DETALLE DE PRODUCTOS Y/O SERVICIOS CONTRATADOS", ln=True, fill=True)

    pdf.set_font("Arial", "", 9)
    total = 0.0
    for articulo in articulos:
        nombre = safe_str(articulo.get("nombre"))
        precio = float(articulo.get("importe") or 0.0)
        total += precio
        pdf.cell(150, 8, nombre, border=0)
        pdf.cell(40, 8, f"${precio:,.2f}", border=0, ln=True, align="R")

    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(150, 8, "IMPORTE TOTAL DEL SERVICIO:", border=0)
    pdf.cell(40, 8, f"${total:,.2f}", border=0, ln=True, align="R")

    tipo_pago = (campos.get("tipo_pago") or "").lower()
    monto = safe_str(campos.get("monto"))
    forma_pago = (campos.get("forma_pago") or "").lower()
    otros = safe_str(campos.get("otros"))

    pdf.set_font("Arial", "B", 9)
    pdf.cell(95, 6, "DETALLES DEL PAGO", ln=True)
    pdf.ln(2)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(22, 6, "ANTICIPO:", ln=0)
    pdf.set_font("Arial", "", 9)
    pdf.cell(28, 6, monto if tipo_pago == "anticipo" else "", border=1)

    pdf.set_font("Arial", "B", 9)
    pdf.cell(25, 6, "PAGO TOTAL:", ln=0)
    pdf.set_font("Arial", "", 9)
    pdf.cell(28, 6, monto if tipo_pago != "anticipo" else "", border=1)

    pdf.set_font("Arial", "B", 9)
    pdf.cell(38, 6, "FECHA LIQUIDACIÓN:", ln=0)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, "", border="B", ln=1)

    pdf.ln(2)
    pdf.cell(35, 6, "FORMA DE PAGO:", ln=0)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(20, 6, "EFECTIVO:", ln=0)
    pdf.set_font("Arial", "", 9)
    pdf.cell(10, 6, "X" if "efectivo" in forma_pago else "", border=1)

    pdf.cell(10)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(20, 6, "TARJETA:", ln=0)
    pdf.set_font("Arial", "", 9)
    pdf.cell(10, 6, "X" if "tarjeta" in forma_pago else "", border=1)

    pdf.cell(10)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(55, 6, "TRANSFERENCIA O DEPÓSITO:", ln=0)
    pdf.set_font("Arial", "", 9)
    pdf.cell(10, 6, "X" if "transferencia" in forma_pago or "depósito" in forma_pago else "", border=1, ln=1)

    pdf.cell(45, 6, "OTROS (ESPECIFIQUE):", ln=0)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, otros, border="B", ln=1)

    try:
        locale.setlocale(locale.LC_TIME, "es_MX.UTF-8")
    except:
        try:
            locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
        except:
            locale.setlocale(locale.LC_TIME, "")

    meses_es = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

    now = datetime.now()
    dia = f"{now.day:02d}"
    mes = meses_es[now.month - 1]
    año = now.year
    fecha_actual = f"el día {dia} de {mes} de {año}"

    pdf.ln(4)
    pdf.set_font("Arial", "", 8)
    pagare_text = (
        f"DEBO Y PAGARÉ incondicionalmente a la orden de YAZMIN ADRIANA HERNÁNDEZ MORENO en Torreón, Coah., "
        f"ó donde exija el tenedor, {fecha_actual}, la cantidad de $ _____________ valor recibido a mi entera "
        "satisfacción. Si no fuera cubierta a su vencimiento la suma que este pagaré expresa, cubriré además el ______ % de interés "
        "mensual desde la fecha de su vencimiento hasta que sea totalmente cubierta, me someto a los tribunales que el tenedor "
        "señale y renuncio al fuero de mi domicilio."
    )

    pdf.multi_cell(0, 4.5, pagare_text, border=1, align="J")

    pdf.ln(2)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, "Acepto Nombre y Firma", ln=True, align="R")

    pdf_str = pdf.output(dest='S')
    pdf_bytes = pdf_str.encode('latin1')
    return pdf_bytes
