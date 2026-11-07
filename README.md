# **1. Requisitos**
1. Python con `uv`.

  En Windows, puedes instalarlo con:
  ```bash
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
  macOS y Linux:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  Revisa si se instalo correctamente ejecutando `uv --version`.
  
2. PostgreSQL
  + Puedes instalarlo en la [página oficial](https://www.postgresql.org/download/).
  + DB Management Tool [DBeaver](https://dbeaver.io/download/). O usar pgAdmin (viene dentro del mismo instalador de PostgreSQL).

3. Pentaho Data Integration (PDI)
  + Puedes descargarlo en la [página oficial](https://www.pentaho.com/download). Se pide una demo gratuita.
# **2. Instalación**
Primero clona el repositorio :
```bash
git clone https://github.com/ablx-ric/dm-trabajo-g2.git
```
Luego entra al directorio del proyecto:
```bash
cd dm-trabajo-g2
```
Finalmente, sincronizamos los paquetes del proyecto con `uv`:
```bash
uv sync
```
Y listo!, los paquetes se instalaran automáticamente.
