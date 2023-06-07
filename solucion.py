import graphene
import requests

class Lugar(graphene.ObjectType):
    nombreLugar = graphene.String()
    latitud = graphene.Float()
    longitud = graphene.Float()

class Clima(graphene.ObjectType):
    lugar = graphene.String()
    latitud = graphene.Float()
    longitud = graphene.Float()
    fecha = graphene.String()
    temperatura_max_diario = graphene.Float()
    temperatura_max_hora = graphene.Float()

class Restaurante(graphene.ObjectType):
    lugar = graphene.String()
    restaurante = graphene.List(graphene.String)

class Query(graphene.ObjectType):
    
    obtener_coordenadas = graphene.Field(Lugar, nombre_lugar=graphene.String())
    obtener_clima = graphene.Field(Clima,nombre_lugar=graphene.String())
    obtener_restaurantes_cercanos = graphene.Field(Restaurante,nombre_lugar=graphene.String())

    print(obtener_coordenadas)

    def resolve_obtener_coordenadas(self, info, nombre_lugar):
        url = f"https://nominatim.openstreetmap.org/search?q={nombre_lugar}&format=json"
        response = requests.get(url)

        data = response.json()
        
        if data:
            latitud = float(data[0]['lat'])
            longitud = float(data[0]['lon'])
            return Lugar(nombreLugar=nombre_lugar, latitud=latitud, longitud=longitud)
        

    def resolve_obtener_clima(self, info, nombre_lugar):
        url = f"https://nominatim.openstreetmap.org/search?q={nombre_lugar}&format=json"

        response = requests.get(url)
        

        data = response.json()

        if data:
            latitud = float(data[0]['lat'])
            longitud = float(data[0]['lon'])
            

            url_diario = f"https://api.open-meteo.com/v1/forecast?latitude={latitud}&longitude={longitud}&forecast_days=2&daily=temperature_2m_max&timezone=PST"
            url_horario = f"https://api.open-meteo.com/v1/forecast?latitude={latitud}&longitude={longitud}&forecast_days=2&hourly=temperature_2m&timezone=PST"

            response_diario = requests.get(url_diario)
            response_horario = requests.get(url_horario)

            data_diario = response_diario.json()
            data_horario = response_horario.json()

            fecha = data_diario['daily']['time'][1]
            clima_diario = data_diario['daily']['temperature_2m_max'][1]
            clima_horario = data_horario['hourly']['temperature_2m'][24]

        
            return Clima(lugar=nombre_lugar,latitud=latitud,longitud=longitud,fecha=fecha,temperatura_max_diario=clima_diario, temperatura_max_hora=clima_horario)
        
    def resolve_obtener_restaurantes_cercanos(self, info, nombre_lugar):

        url = f"https://nominatim.openstreetmap.org/search?q={nombre_lugar}&format=json"
        response = requests.get(url)

        data = response.json()
        
        if data:
            latitud = float(data[0]['lat'])
            longitud = float(data[0]['lon'])

        bbox = f"{float(longitud)-0.01},{float(latitud)-0.01},{float(longitud)+0.01},{float(latitud)+0.01}"
        url = f"https://api.openstreetmap.org/api/0.6/map.json?bbox={bbox}"
        response = requests.get(url)
        print(response.status_code)
        if response.status_code == 200:
            data = response.json()
            lugares_cercanos = []
            
            if 'elements' in data:
                elementos = data['elements']
                
                for elemento in elementos:
                    if 'tags' in elemento and 'amenity' in elemento['tags'] and elemento['tags']['amenity'] == 'restaurant':
                        if 'name' in elemento['tags']:
                            lugares_cercanos.append(elemento['tags']['name'])
            
            return Restaurante(lugar=nombre_lugar,restaurante=lugares_cercanos)
          
    
        

schema = graphene.Schema(query=Query)

consulta = '''
 query {
     obtenerCoordenadas(nombreLugar: "jesus maria lima")
     {
         nombreLugar
         latitud
         longitud
     }
     obtenerClima(nombreLugar: "jesus maria lima")
     {
        lugar
        latitud
        longitud
        fecha
        temperaturaMaxDiario
        temperaturaMaxHora
     }
 }
'''

consulta2 = '''
 query {
     obtenerClima(nombreLugar: "jesus maria lima")
     {
        lugar
        latitud
        longitud
        fecha
        temperaturaMaxDiario
        temperaturaMaxHora
     }
 }
'''


consulta3 = '''
 query {
     obtenerRestaurantesCercanos(nombreLugar: "jesus maria lima")
     {
        lugar
        restaurante
     }
 }
'''


resultado = schema.execute(consulta)
print(resultado.data)
print(resultado.errors)

resultado2 = schema.execute(consulta2)
print(resultado2.data)
print(resultado2.errors)

resultado3 = schema.execute(consulta3)
print(resultado3.data)
print(resultado3.errors)

