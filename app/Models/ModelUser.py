from.entities.user import User

class ModuleUser():
    @classmethod
    def login(self,db,user):
        try:
            cur=db.cursor()
            sql="SELECT id_usuario,nombre_usuario,contrasenia_usuario,estado FROM usuarios WHERE estado='True' and nombre_usuario='{}'".format(user.nombre_usuario)
            cur.execute(sql)
            row=cur.fetchone()
            if row != None:
                user=User(row[0], row[1],user.check_password(row[2],user.contrasenia),None)
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(self,db,id_usuario):
        try:
            cur=db.cursor()
            sql="SELECT id_usuario,nombre_usuario,contrasenia_usuario FROM usuarios WHERE estado='True' and id_usuario='{}'".format(id_usuario)
            cur.execute(sql)
            row=cur.fetchone()
            if row !=None:
                return User(row[0], row[1], None, row[2])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)