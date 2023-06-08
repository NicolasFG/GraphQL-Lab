const express = require('express');
const { graphqlHTTP } = require('express-graphql');
const { buildSchema } = require('graphql');
const axios = require('axios');
//Recuerden instalar las dependencias ...
// Definición del esquema de GraphQL
const schema = buildSchema(`
  type Lugar {
    nombreLugar: String
    latitud: Float
    longitud: Float
  }

  type Clima {
    lugar: String
    latitud: Float
    longitud: Float
    fecha: String
    temperatura_max_diario: Float
    temperatura_max_hora: Float
  }

  type Restaurante {
    lugar: String
    restaurante: [String]
  }

  type Query {
    obtener_coordenadas(nombre_lugar: String): Lugar
    obtener_clima(nombre_lugar: String): Clima
    obtener_restaurantes_cercanos(nombre_lugar: String): Restaurante
  }
`);

// Implementación de las resolvers
const root = {
  obtener_coordenadas: async ({ nombre_lugar }) => {
    const url = `https://nominatim.openstreetmap.org/search?q=${nombre_lugar}&format=json`;
    const response = await axios.get(url);

    const data = response.data;

    if (data.length > 0) {
      const { lat, lon } = data[0];
      const latitud = parseFloat(lat);
      const longitud = parseFloat(lon);
      return { nombreLugar: nombre_lugar, latitud, longitud };
    }

    return null;
  },

  obtener_clima: async ({ nombre_lugar }) => {
    const url = `https://nominatim.openstreetmap.org/search?q=${nombre_lugar}&format=json`;
    const response = await axios.get(url);

    const data = response.data;

    if (data.length > 0) {
      const { lat, lon } = data[0];
      const latitud = parseFloat(lat);
      const longitud = parseFloat(lon);

      const url_diario = `https://api.open-meteo.com/v1/forecast?latitude=${latitud}&longitude=${longitud}&forecast_days=2&daily=temperature_2m_max&timezone=PST`;
      const url_horario = `https://api.open-meteo.com/v1/forecast?latitude=${latitud}&longitude=${longitud}&forecast_days=2&hourly=temperature_2m&timezone=PST`;

      const response_diario = await axios.get(url_diario);
      const response_horario = await axios.get(url_horario);

      const data_diario = response_diario.data;
      const data_horario = response_horario.data;

      const fecha = data_diario.daily.time[1];
      const clima_diario = data_diario.daily.temperature_2m_max[1];
      const clima_horario = data_horario.hourly.temperature_2m[24];

      return {
        lugar: nombre_lugar,
        latitud,
        longitud,
        fecha,
        temperatura_max_diario: clima_diario,
        temperatura_max_hora: clima_horario
      };
    }

    return null;
  },

  obtener_restaurantes_cercanos: async ({ nombre_lugar }) => {
    const url = `https://nominatim.openstreetmap.org/search?q=${nombre_lugar}&format=json`;
    const response = await axios.get(url);

    const data = response.data;

    if (data.length > 0) {
      const { lat, lon } = data[0];
      const latitud = parseFloat(lat);
      const longitud = parseFloat(lon);

      const bbox = `${longitud - 0.01},${latitud - 0.01},${longitud + 0.01},${latitud + 0.01}`;
      const url = `https://api.openstreetmap.org/api/0.6/map.json?bbox=${bbox}`;
      const response = await axios.get(url);

      if (response.status === 200) {
        const data = response.data;
        const lugares_cercanos = [];

        if ('elements' in data) {
          const elementos = data.elements;

          for (const elemento of elementos) {
            if ('tags' in elemento && 'amenity' in elemento.tags && elemento.tags.amenity === 'restaurant') {
              if ('name' in elemento.tags) {
                lugares_cercanos.push(elemento.tags.name);
              }
            }
          }
        }

        return { lugar: nombre_lugar, restaurante: lugares_cercanos };
      }
    }

    return null;
  }
};

// Creación de la aplicación Express
const app = express();

// Configuración de la ruta GraphQL
app.use(
  '/graphql',
  graphqlHTTP({
    schema: schema,
    rootValue: root,
    graphiql: true
  })
);

// Iniciar el servidor
app.listen(3000, () => {
  console.log('Servidor GraphQL en ejecución en http://localhost:3000/graphql');
});
