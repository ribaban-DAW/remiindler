# remiindler

## 🚀 Descripción

Simple script para **recordar** cualquier asignatura que falte por entregar en **Moodle**. Escrito en Python usando [Selenium](https://www.selenium.dev/).

> [!NOTE]
> Los IDS y las URLs están hardcodeados para mis asignaturas :rofl:

## 🏡 Setup

> [!NOTE]
>
> Esto es opcional, lo puedes proporcionar mientras se ejecuta el programa.

Crea un archivo `.env` siguiendo el `.env.example`
```
ENV_USERNAME=your_username
ENV_PASSWORD=your_password
```

> [!NOTE]
> Si usas caracteres especiales como `'`, `"`, `\`, `#`, añade un `\` antes.
> Por ejemplo:
> ```
> 'Hello'World
> ```
> Pasaría a ser
> ```
> \'Hello\'World
> ```

### Windows

1. Crea el entorno virtual
```
python3 -m venv venv
```

2. Activa el entorno virtual
```
venv/Scripts/activate
```

> [!NOTE]
> Si esto falla, quizá tengas que ejecutar el siguiente comando.
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Una vez hecho esto, inténtalo de nuevo.
> Referencia: https://docs.python.org/3/library/venv.html#creating-virtual-environments

3. Instala las dependencias
```
python3 -m pip install -r requirements.txt
```

4. Ejecuta el script
```
python3 main.py
```

### Linux

1. Crea un entorno virtual
```
python3 -m venv venv
```

2. Activa el entorno virtual
```
source venv/bin/activate
```

3. Instala las dependencias
```
python3 -m pip install -r requirements.txt
```

4. Ejecuta el script
```
python3 main.py
```

## Contribución

Si encuentras algún bug o tienes alguna sugerencia, puedes abrir un [issue](https://github.com/ribaban-DAW/remiindler/issues/new).
