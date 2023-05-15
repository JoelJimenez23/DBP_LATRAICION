import os

# Obtiene el usuario y la contraseña de las variables de entorno
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')

print(db_user)
print(db_password)
# ...
"""
Para que cada uno trabaje en su maquina:

Sigue estos pasos para establecer correctamente las variables de entorno en Windows:

1. Abre el menú de inicio y busca "Editar las variables de entorno del sistema". 
Haz clic en el resultado de búsqueda correspondiente para abrir la ventana de Propiedades del sistema.

2. En la pestaña "Opciones avanzadas", haz clic en el botón "Variables de entorno".

3. En la sección "Variables del sistema", encontrarás la lista de variables de entorno existentes. 
Puedes hacer clic en "Nueva..." para agregar una nueva variable de entorno.

4. En el campo "Nombre de la variable", ingresa el nombre de la variable, como "DB_USER".

5. En el campo "Valor de la variable", ingresa el valor correspondiente, como tu nombre de usuario de PostgreSQL.

6. Haz clic en "Aceptar" para guardar la nueva variable de entorno.

7. Repite los pasos anteriores para establecer la variable de entorno `DB_PASSWORD` con su respectivo valor.

Una vez que hayas establecido las variables de entorno correctamente, podrás acceder a ellas 
en tu código Python utilizando `os.environ.get()` como se mencionó anteriormente:

Asegúrate de reiniciar tu entorno de desarrollo o terminal después de establecer 
las variables de entorno para que los cambios surtan efecto y puedan ser accesibles en tu código.
"""