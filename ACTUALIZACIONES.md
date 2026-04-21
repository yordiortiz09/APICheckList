# Guia para publicar una nueva version de la app

Cuando tengas cambios nuevos en la app Flutter y quieras que los usuarios reciban el aviso de "Nueva version disponible", sigue estos pasos.

## 1. Subir la version en el proyecto Flutter

En el repo de Flutter, abre `pubspec.yaml` y sube el numero de version.

Formato: `versionName+versionCode`

- `versionName` es lo que se muestra y compara (ej. `1.2.0`)
- `versionCode` es un entero que Android usa internamente y siempre debe subir (ej. `+3`)

Ejemplo de cambio:

```yaml
# Antes
version: 1.1.0+2

# Despues
version: 1.2.0+3
```

## 2. Compilar el APK

Desde la raiz del proyecto Flutter:

```bash
flutter build apk --release
```

El APK queda en: `build/app/outputs/flutter-apk/app-release.apk`

## 3. Subir el APK al servidor

Copia el APK a esta ruta del servidor, reemplazando el anterior:

```
C:\Users\Yordi\Desktop\api\static\apk\cremapet.apk
```

IMPORTANTE: el archivo debe llamarse exactamente `cremapet.apk`.

## 4. Actualizar la version en la API

En el servidor, edita el archivo:

```
C:\Users\Yordi\Desktop\api\app\routes\actualizaciones.py
```

Modifica estas tres variables:

```python
APP_VERSION = '1.2.0'                 # debe coincidir con el versionName del pubspec
FORZAR_ACTUALIZACION = False          # True si quieres que el usuario no pueda saltarse la actualizacion
NOTAS_VERSION = 'Descripcion de los cambios de esta version.'
```

### Cuando usar `FORZAR_ACTUALIZACION = True`

Solo para cambios criticos donde versiones viejas ya no deben seguir funcionando:

- Cambios de esquema incompatibles en la BD
- Correcciones de seguridad
- Nuevos endpoints que la app vieja no conoce

En ese caso el dialogo no tendra boton de "Mas tarde", solo "Descargar".

## 5. Reiniciar el servicio de la API

Abre PowerShell o CMD como administrador y ejecuta:

```
nssm restart ApiFlask
```

Verifica que este corriendo:

```
nssm status ApiFlask
```

Debe decir `SERVICE_RUNNING`.

## 6. Verificar

Desde cualquier navegador o desde tu laptop:

```
http://Grupo-str.zapto.org:5000/app/version
```

Deberia responder con el JSON actualizado:

```json
{
  "version": "1.2.0",
  "url_descarga": "/app/descargar",
  "forzar_actualizacion": false,
  "notas": "Descripcion de los cambios de esta version."
}
```

## 7. Probar en el celular

Abre la app en tu celular. Debe aparecer el dialogo:

**Nueva version disponible (1.2.0)**

Con los botones "Mas tarde" y "Descargar".

---

## Resumen rapido

1. `pubspec.yaml` -> sube version
2. `flutter build apk --release`
3. Copia APK a `C:\Users\Yordi\Desktop\api\static\apk\cremapet.apk`
4. Edita `APP_VERSION` y `NOTAS_VERSION` en `actualizaciones.py`
5. `nssm restart ApiFlask`

---

## Notas importantes

- Si la `APP_VERSION` de la API es igual o menor que la del APK instalado, no sale el dialogo.
- El archivo APK debe llamarse `cremapet.apk` exactamente. Si cambias el nombre, hay que ajustar `APK_FILENAME` en `actualizaciones.py`.
- Siempre incrementa el `versionCode` (`+N`) del pubspec, si no Android no permite instalar la nueva version sobre la anterior.
- Los usuarios que aun no tengan esta primera version con la logica de actualizacion necesitan recibir el APK manualmente una ultima vez.
