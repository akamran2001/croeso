/**
 * Hide the caption of the gallery when hovering on the image
 * @param {number} id
 */
const hide_caption = (id) => {
  document.getElementById(id).style.opacity = 0;
};
/**
 * Show the caption of the gallery when not hovering on the image
 * @param {number} id
 */
const show_caption = (id) => {
  document.getElementById(id).style.opacity = 1;
};
/**
 * Color the hovered tags
 * @param {Event} event
 */
const tag_hover = (event) => {
  event.currentTarget.style.background = "#00B74A";
};
/**
 * Reset the bg color of the hovered tags
 * @param {Event} event
 */
const tag_hover_end = (event) => {
  event.currentTarget.style.background = "rgba(83, 83, 83, 0.4)";
};
/**
 * Get the lat and lon of the map from URL, and configure the zoom accordingly for the map
 * @returns {{lat: string, lon: number, zoom: number}} Configuration of map
 */
const get_map_config = () => {
  const params = new URLSearchParams(location.search);
  const config = {
    lat: parseFloat(params.get("lat")),
    lon: parseFloat(params.get("lon")),
    zoom: 16,
  };

  if (config.lat === null || config.lon == null) {
    //Default to Lat and Lon of Wales if error in data
    config.lat = 52.2928116;
    config.lon = -3.73893;
    config.zoom = 5;
  }

  return config;
};
/**
 * Hide the loading bars and display the map when all the data is ready
 */
const display_map = () => {
  map_config = get_map_config();
  document.getElementById("map").style.height = "400px";
  const map = new ol.Map({
    target: "map",
    layers: [
      new ol.layer.Tile({
        source: new ol.source.OSM(),
      }),
    ],
    view: new ol.View({
      center: ol.proj.fromLonLat([map_config.lon, map_config.lat]),
      zoom: map_config.zoom,
    }),
  });
  document.getElementById("loader").style.display = "none";
};

window.addEventListener("load", display_map);
