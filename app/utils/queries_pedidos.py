# app/utils/queries_pedidos.py

def get_datos_pedido():
    return """
    SELECT p.clave, p.fecha, p.hora, p.referencia, entidades.descripcion AS sucursal,
           cs.sc_nombre AS cliente, cs2.sc_nombre AS recolector, p.comment
    FROM pedidos p
    LEFT OUTER JOIN entidades ON p.clvent = entidades.clave
    LEFT OUTER JOIN cat_sujcolectivos cs ON p.scc_clave = cs.sc_clave
    LEFT OUTER JOIN cat_sujcolectivos cs2 ON p.scp_clavevendedor = cs2.sc_clave
    WHERE p.cancelado = 0 AND p.clave = :pedido
    """

def get_articulos_pedido():
    return """
    SELECT pedidosartic.clave, pedidosartic.clvarticulo, articuloventa.nombre AS articulo,
           ROUND((pedidosartic.cantidadalter * pedidosartic.precioalter) + 
                 ((pedidosartic.cantidadalter * pedidosartic.precioalter) * 0.16)) AS importe
    FROM pedidosartic
    LEFT OUTER JOIN articuloventa ON pedidosartic.clvarticulo = articuloventa.clave
    WHERE pedidosartic.clvventa = :pedido
    """

def get_valor_campo():
    return """
    SELECT pedidoscampos.pc_valor
    FROM pedidoscampos
    WHERE pedidoscampos.pc_claveventa = :pedido
      AND pedidoscampos.cc_clavecampo = :campo_id
    """


CAMPOS_PEDIDO = {
    "mascota": 13,
    "veterinario": 14,
    "raza": 15,
    "peso": 16,
    "edad": 17,
    "causa": 18,
    "contratante": 19,
    "contacto": 20,
    "lugar": 21,
    "domicilio": 22,
    "telefono": 23,
    "tipo_pago": 4,
    "monto": 1,
    "forma_pago": 25,
    "otros": 26,
}


