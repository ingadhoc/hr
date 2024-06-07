from odoo import api, fields, models, _
from datetime import timedelta, datetime
import calendar

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def ultimo_dia_del_mes(self, fecha):
        # Obtenemos ulitmo día del mes a partir de la fecha y usando la funcion monthrange:
        year = fecha.year
        month = fecha.month
        ultimo_dia = calendar.monthrange(year, month)[1]
        # Creamos una nueva fecha con el último día del mes, manteniendo los demas datos de la fecha:
        return fecha.replace(day=ultimo_dia)

    def split_days(self, rec):
        registros_nuevos = []
        date_from = rec['request_date_from']
        original_date_to = rec['request_date_to']

        while date_from <= original_date_to:
            #calculamos el último día del mes llamando a ese método, para luego compararlo con la fecha de fin de ausencia, original_date_to
            fin_mes = self.ultimo_dia_del_mes(date_from)
            #si la fecha de fin de ausencia, original_date_to está dentro del mes de inicio:
            if original_date_to <= fin_mes:
                #guardamos las fechas del único registro a crear
                registros_nuevos.append({
                    'request_date_from': date_from,
                    'request_date_to': original_date_to,
                })
                break
                # date_from = original_date_to
            else:
                # guardamos las fechas de cada registro a crear hasta llegar a la fecha de fin de ausencia, original_date_to
                registros_nuevos.append({ 
                    'request_date_from': date_from,
                    'request_date_to': fin_mes,
                })
                # pasamos al primer dia del mes siguiente para volver a entrar en el while:
                date_from = fin_mes + timedelta(days=1)

        return registros_nuevos

    
    @api.model_create_multi
    def create(self, vals_list):
        nuevos_vals_list = []
        for vals in vals_list:
            date_from = vals.get('request_date_from')
            date_to = vals.get('request_date_to')

            if date_from and date_to:
                # Convertir a objetos datetime si son cadenas (no debería, pero si no lo hacía no funcionaba)
                if isinstance(date_from, str):
                    date_from = fields.Datetime.from_string(date_from)
                if isinstance(date_to, str):
                    date_to = fields.Datetime.from_string(date_to)
            
            # comparamos la fecha de fin de la ausencia con la fecha de ultimo día del mes
            # Si la ausencia termina en otro mes más adelante, llamamos al metodo split_days() para que calcule las fechas en las que dividir las ausencias:
            if date_to > self.ultimo_dia_del_mes(date_from):
                registros_divididos = self.split_days({
                    'request_date_from' : date_from,
                    'request_date_to' : date_to,
                })
                # creamos una copia de los valores originales para cada registro dividido:
                for rec in registros_divididos:
                    nuevo_vals = vals.copy()
                    nuevo_vals.update(rec)
                    nuevos_vals_list.append(nuevo_vals)
            #si la ausencia termina en el mismo mes en el que comienza, solo se agrega el registro original vals a la lista nueva de vals
            else:
                nuevos_vals_list.append(vals)

        return super().create(nuevos_vals_list)
    
