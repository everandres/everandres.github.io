"""Builds the project pages (portfolio-single-*.html) from one shared shell.

The Untree "Minimal" template loads each project page by AJAX and injects only
its `.portfolio-single-wrap` block, so every page keeps that structure. This
script owns the nav and footer of all project pages so they stay identical.

Run from the repo root:  python3 tools/build_pages.py
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HEAD = """<!doctype html>
<html lang="en">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <meta name="author" content="Ever Andrés Salazar Mercado">
  <link rel="shortcut icon" href="favicon.png">
  <meta name="description" content="{desc}">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=PT+Mono&display=swap" rel="stylesheet">

  <link rel="stylesheet" href="css/bootstrap.min.css">
  <link rel="stylesheet" href="css/owl.carousel.min.css">
  <link rel="stylesheet" href="css/owl.theme.default.min.css">
  <link rel="stylesheet" href="css/jquery.fancybox.min.css">
  <link rel="stylesheet" href="fonts/icomoon/style.css">
  <link rel="stylesheet" href="fonts/flaticon/font/flaticon.css">
  <link rel="stylesheet" href="css/aos.css">
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="css/additions.css">

  <title>{title} · Ever Salazar</title>
</head>

<body data-spy="scroll" data-target=".site-navbar-target" data-offset="100">

  <div class="site-mobile-menu site-navbar-target">
    <div class="site-mobile-menu-header">
      <div class="site-mobile-menu-close">
        <span class="icofont-close js-menu-toggle"></span>
      </div>
    </div>
    <div class="site-mobile-menu-body"></div>
  </div>

  <nav class="site-nav dark mb-5 site-navbar-target">
    <div class="container">
      <div class="site-navigation">
        <a href="index.html" class="logo m-0">Ever Andrés<span class="text-primary">.</span></a>
        <ul class="js-clone-nav d-none d-lg-inline-none site-menu float-right site-nav-wrap">
          <li><a href="index.html#home-section" class="nav-link">Home</a></li>
          <li><a href="index.html#portfolio-section" class="nav-link">Work</a></li>
          <li><a href="index.html#about-section" class="nav-link">About</a></li>
          <li><a href="index.html#contact-section" class="nav-link">Contact</a></li>
        </ul>
        <a href="#" class="burger ml-auto float-right site-menu-toggle js-menu-toggle d-inline-block d-lg-inline-block" data-toggle="collapse" data-target="#main-navbar">
          <span></span>
        </a>
      </div>
    </div>
  </nav>

  <div class="untree_co-section untree_co-section-4 pb-0" id="portfolio-section">
    <div class="container">
      <div class="portfolio-single-wrap unslate_co--section" id="portfolio-single-section">
        <div class="portfolio-single-inner">
"""

TAIL = """        </div>
      </div>
    </div>
  </div>

{footer}

  <script src="js/jquery-3.4.1.min.js"></script>
  <script src="js/popper.min.js"></script>
  <script src="js/bootstrap.min.js"></script>
  <script src="js/owl.carousel.min.js"></script>
  <script src="js/jquery.animateNumber.min.js"></script>
  <script src="js/jquery.waypoints.min.js"></script>
  <script src="js/jquery.fancybox.min.js"></script>
  <script src="js/aos.js"></script>
  <script src="js/wave-animate.js"></script>
  <script src="js/circle-progress.js"></script>
  <script src="js/imagesloaded.pkgd.js"></script>
  <script src="js/isotope.pkgd.min.js"></script>
  <script src="js/jquery.easing.1.3.js"></script>
  <script src="js/TweenMax.min.js"></script>
  <script src="js/ScrollMagic.min.js"></script>
  <script src="js/scrollmagic.animation.gsap.min.js"></script>
  <script src="js/custom.js"></script>
</body>

</html>
"""

FOOTER = """  <div class="site-footer">
    <div class="container">
      <div class="row">
        <div class="col-lg-6">
          <div class="widget">
            <h3>Connect</h3>
            <ul class="list-unstyled social">
              <li><a href="https://www.linkedin.com/in/ever-salazar/" aria-label="LinkedIn"><span class="icon-linkedin"></span></a></li>
              <li><a href="https://github.com/everandres" aria-label="GitHub"><span class="icon-github"></span></a></li>
              <li><a href="mailto:andressalmercado@gmail.com" aria-label="Email"><span class="icon-envelope"></span></a></li>
            </ul>
          </div>
        </div>
      </div>
      <div class="row mt-5">
        <div class="col-12 text-center">
          <p class="mb-0">&copy; 2026 Ever Andrés Salazar Mercado &mdash; Template &ldquo;Minimal&rdquo; by <a href="https://untree.co">Untree.co</a> (<a href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>)</p>
        </div>
      </div>
    </div>
  </div>"""


def figure(src, caption):
    if src.endswith(".mp4"):
        media = (f'<video src="{src}" class="img-fluid" autoplay muted loop playsinline '
                 f'preload="metadata" aria-label="{caption}"></video>')
    else:
        media = f'<img src="{src}" alt="{caption}" class="img-fluid">'
    return f"""                <figure class="mb-4">
                  {media}
                  <figcaption>{caption}</figcaption>
                </figure>"""


def details(items):
    cols = []
    for label, val in items:
        cols.append(f"""                <div class="col-sm-6 col-md-6 col-lg-3">
                  <div class="detail-v1">
                    <span class="detail-label">{label}</span>
                    <span class="detail-val">{val}</span>
                  </div>
                </div>""")
    return "\n".join(cols)


def body(p):
    figs = "\n".join(figure(s, c) for s, c in p["figures"])
    left = "\n".join(f"              <p>{t}</p>" for t in p["left"])
    right = "\n".join(f"              <p>{t}</p>" for t in p["right"])
    return f"""          <h2 class="heading-portfolio-single-h2 text-black">{p['title']}</h2>

          <div class="row justify-content-between mb-5">
            <div class="col-12 mb-4">
              <div class="owl-carousel single-slider">
{figs}
              </div>
            </div>

            <div class="col-12 my-5">
              <div class="row">
{details(p['details'])}
              </div>
            </div>

            <div class="col-md-6">
{left}
            </div>
            <div class="col-md-6">
{right}
            </div>
          </div>
"""


def link(href, text):
    return f'<a href="{href}">{text}</a>'


IDEAM_REPOS = [
    ("Actualizacion_datos_hidrometeorologicos", "daily update of hydrometeorological data"),
    ("Hidrologia_automaticas", "river level and flow from automatic stations"),
    ("Categorizacion_anomalias", "precipitation anomaly categories"),
    ("Categorizar_cuencas", "classification by river basin"),
    ("Actualizacion_volcanes", "WRF wind forecasts over active volcanoes"),
    ("Mapa_estaciones_automaticas", "maps of automatic stations"),
    ("Dashboard_Calendograma", "precipitation calendar dashboard"),
    ("VisorAlertas", "alert map viewer"),
]
repo_list = "<br>".join(
    f'{link("https://github.com/everandres/" + r, r)}: {d}' for r, d in IDEAM_REPOS)

PAGES = {
    5: dict(
        title="Forecasts &amp; alerts at IDEAM",
        desc="Three years at IDEAM's Forecasting and Alerts Office (OSPA), Colombia's national weather service.",
        figures=[
            ("images/port_1.png", "Maximum temperature and its monthly average for the main cities of Colombia."),
            ("images/port_7.png", "Automatic weather stations and their precipitation for the last meteorological day."),
            ("images/port_3.png", "Air quality monitoring report dashboard for Medellín."),
            ("images/port_4.png", "Calendar dashboard: accumulated precipitation per day of the year at one station."),
            ("images/port_5.png", "Precipitation anomaly and total precipitation against the multi-year average."),
            ("images/port_6.png", "IDW interpolation of precipitation at conventional stations."),
            ("images/port_8.png", "Maximum temperature estimated from NetCDF data."),
            ("images/port_9.png", "Station catalogue and daily river levels compared with historical El Niño and La Niña years."),
        ],
        details=[
            ("Dates", "June 2021 &ndash; April 2024"),
            ("Role", "Hydrometeorological Data Analyst"),
            ("Office", "Forecasting and Alerts Office (OSPA)"),
            ("Visit", link("https://www.ideam.gov.co/", "IDEAM")),
        ],
        left=[
            "For three years I worked at IDEAM's Forecasting and Alerts Office (OSPA), the operational center that issues Colombia's official weather forecasts and hydrometeorological alerts. I managed the hydrometeorological data behind the national early-warning system, and issued weather forecasts and hydrological, landslide and wildfire alerts for the whole country.",
            "Every day I received and validated data from automatic and conventional stations and from external networks: correcting anomalous values, filling gaps, reporting station failures and building multi-year time series and climatologies.",
        ],
        right=[
            "I automated the office's daily data routines in Python and SQL, and built a web map and dashboards to follow the alerts. Some of those scripts are public:",
            repo_list,
            "The images on this page are maps and dashboards I made during those years.",
        ],
    ),
    6: dict(
        title="Lightning, forecasts &amp; early warning",
        desc="Geospatial data engineering at Keraunos: satellite and forecast pipelines, real-time lightning risk.",
        figures=[("media/keraunos-banner.jpg", "Keraunos, 2024 to today. The platform is private, so there are no screenshots here.")],
        details=[
            ("Dates", "May 2024 &ndash; Present"),
            ("Role", "Geospatial Data Engineer (until July 2026, Developer &ndash; Data Analyst)"),
            ("Stack", "Python, xarray, Zarr/STAC, PostGIS, Kafka, FastAPI/TiTiler, MapLibre"),
            ("Visit", link("https://keraunos.co", "keraunos.co")),
        ],
        left=[
            "Keraunos is a lightning-research and detection company that operates the LINET network in Colombia. I contribute to Predicthor, its real-time platform that relates lightning to asset monitoring and weather forecasts. The platform and its data are private, so this page describes the work instead of showing it.",
            "<strong>Forecast data.</strong> I re-architected the ECMWF IFS pipeline from GRIB into an analysis-ready Zarr datacube with a STAC catalog: sub-grids merged without interpolation, separate chunk layouts for maps and time series (one chunk read instead of 90) and publishing without downtime. On top of it I built a FastAPI/TiTiler service that packs physical values into 24-bit RGB tiles and decodes them on the GPU.",
            "<strong>Satellites.</strong> GOES-16/19 pipelines that turn all 16 ABI bands into Cloud-Optimized GeoTIFFs, with per-band calibration and cloud-cover alerts for each asset.",
        ],
        right=[
            "<strong>Spatial accuracy.</strong> In a multi-model precipitation ensemble (ECMWF, GFS, WRF) I found that WRF's irregular latitude spacing shifted its northern edge by 8.2&nbsp;km. I moved the computation onto the true coordinates and implemented conservative regridding to a common 0.1&deg; grid.",
            "<strong>Real time.</strong> I designed MPSR, a Kafka streaming model that scores lightning outage risk for each transmission tower, and hardened the alerting engine so its state survives restarts and every notification is sent once. Spatial SQL in PostGIS measures lightning exposure around every asset in a single batched query.",
            "<strong>Web mapping.</strong> I built SIMK, a weather platform, almost single-handedly: model fields rendered as WebGL textures in MapLibre, vector tiles from PostGIS and a Docker stack.",
        ],
    ),
    7: dict(
        title="El Ni&ntilde;o breathes over Colombia",
        desc="Data storytelling: how ENSO moves Colombian reservoirs, coffee, vegetation and more, 2000–2025.",
        figures=[
            ("media/oni-1.jpg", "Opening of the piece (in Spanish)."),
            ("media/oni-3.jpg", "Radial chart: 26 years of ONI around the country, one ring per year and one sector per month."),
            ("media/oni-2.jpg", "Real variables around the clock, with their lag correlation and confidence interval."),
        ],
        details=[
            ("Year", "2026"),
            ("Role", "Data, design and code"),
            ("Stack", "Python, Next.js, D3, MapLibre"),
            ("Visit", link("oni/", "See the piece")),
        ],
        left=[
            "A data-storytelling piece about how the Oceanic Niño Index (ONI) moves, in sync and with lag, expected and unexpected Colombian variables between 2000 and 2025: reservoirs and energy prices, coffee production, vegetation, chlorophyll in the Pacific, humpback whale sightings and homicide rates.",
            "Its centerpiece is a radial chart: 26 years of ONI wrapped around the country, red when the Pacific warms and blue when it cools, with the variables drawn as veins around it.",
        ],
        right=[
            "Lag correlations carry 95% confidence intervals from a circular block bootstrap with Bartlett's effective sample size. A relationship is only marked as significant when the interval does not cross zero.",
            "ONI (NOAA CPC), reservoirs and energy prices (XM), coffee (Federaci&oacute;n Nacional de Cafeteros) and homicides are real data. Vegetation, chlorophyll and whales are still modeled from the literature and are labeled that way on the page until the primary sources (MODIS, GBIF) are in.",
        ],
    ),
    8: dict(
        title="2026 World Cup travel routes",
        desc="Open dataset and animated map of the routes of all 48 teams in the 2026 World Cup.",
        figures=[
            ("media/mundial-1.jpg", "The tournament replayed day by day, with a live ranking of kilometres travelled."),
            ("media/mundial-2.jpg", "Opening day: 48 teams at their base camps."),
        ],
        details=[
            ("Dates", "June &ndash; July 2026"),
            ("Role", "Dataset, design and code"),
            ("Stack", "Python, Next.js, deck.gl, MapLibre"),
            ("Visit", link("https://everandres.github.io/mundial-2026-recorridos/", "Live map") + " &middot; " + link("https://github.com/everandres/mundial-2026-recorridos", "Repository")),
        ],
        left=[
            "An open, reproducible dataset of the routes travelled by the 48 teams of the 2026 World Cup across its 104 matches, from their base camps to the city where they were knocked out.",
            "Each leg follows FIFA's logistics: in the group stage teams fly from their base camp to each venue and back; from the round of 32 on they travel city to city.",
        ],
        right=[
            "Distances are geodesic (haversine), with per-leg and cumulative metrics for every team: total kilometres, longest and shortest leg, cities and countries visited.",
            "The site replays the tournament day by day on an animated deck.gl and MapLibre map.",
        ],
    ),
    9: dict(
        title="Exploded axonometry of a map",
        desc="A map taken apart like an architectural drawing: custom deck.gl shader layers over PMTiles.",
        figures=[
            ("media/axonometria.mp4", "From the globe to the exploded view."),
            ("media/axonometria-1.jpg", "The stack rotated: place names, boundaries, urban fabric, roads and hydrography."),
            ("media/axonometria-2.jpg", "A system shown as a plan sheet, with scale bar, legend and corner coordinates."),
            ("media/axonometria-3.jpg", "The collapsed stack: a conventional map, one ink on paper."),
        ],
        details=[
            ("Year", "2026"),
            ("Role", "Concept, design and code"),
            ("Stack", "Next.js, deck.gl custom shader layers, PMTiles, Web Workers"),
            ("Visit", "Video above"),
        ],
        left=[
            "Architecture portfolios explain buildings with exploded axonometric drawings. This project applies that language to a map. The object taken apart is not the territory but the map itself, separated into the systems that make it up (hydrography, roads, urban fabric, boundaries and place names) and stacked as parallel sheets that collapse back into a normal map.",
            "You enter through the planet as a sphere. Zooming in morphs the projection from sphere to plane, and from zoom 10 a button opens the exploded view, where the stack can be orbited and pulled apart. Each system can also be shown as a plan sheet.",
        ],
        right=[
            "There is no backend. Tiles come straight from a planet-wide PMTiles file over HTTP range requests, city blocks are derived on the fly in a web worker, and the morph between sphere and plane happens in custom deck.gl shader layers.",
            "No color and no building extrusion: one ink on paper, with hierarchy coming only from line weight and opacity. The vertical axis means &ldquo;belongs to this layer&rdquo; and nothing else.",
        ],
    ),
    10: dict(
        title="Cartolens: 3D relief maps",
        desc="Cartolens turns elevation maps of Colombian departments into 3D relief you can print.",
        figures=[("media/cartolens-1.jpg", "A department's terrain rebuilt in 3D, colored by elevation.")],
        details=[
            ("Year", "2024"),
            ("Role", "Design and development"),
            ("Stack", "Next.js, three.js / React Three Fiber, Express, MongoDB, Fly.io"),
            ("Visit", link("https://cartolens.com/", "cartolens.com")),
        ],
        left=[
            "Cartolens turns elevation maps into 3D relief. You pick a Colombian department, or upload your own height map, and the terrain is rebuilt in the browser: elevation displaces a mesh and a custom shader colors it by height.",
            "Each model can be downloaded as an STL file (a 512 &times; 512 mesh), ready for 3D printing.",
        ],
        right=[
            "Behind it is a small Express and MongoDB API on Fly.io that serves the catalogue of departments with their profile (capital, population, elevation range, main rivers, typical food) and stores the images.",
        ],
    ),
    11: dict(
        title="Bogot&aacute;'s urban trees",
        desc="Map of the 1.47 million trees of Bogotá's public tree census, served as a single PMTiles file.",
        figures=[("media/arbolado-1.jpg", "Trees of the census over the city, with the mini-map in the corner.")],
        details=[
            ("Year", "2026"),
            ("Role", "Data processing, design and code"),
            ("Stack", "PMTiles, MapLibre, Next.js"),
            ("Visit", link("arbolado/", "See the map")),
        ],
        left=[
            "A map of the 1,473,588 trees in Bogot&aacute;'s public tree census, 423 species, from the open data of the Jard&iacute;n Bot&aacute;nico de Bogot&aacute;.",
            "I converted the official shapefile into vector tiles packed in a single PMTiles file, so the whole city loads from static hosting, with no tile server, over HTTP range requests.",
        ],
        right=[
            "A statistics panel summarizes species and heights (the most common tree is the sauco, and the average height is 4.2&nbsp;m), and a mini-map keeps you oriented in the city.",
        ],
    ),
    12: dict(
        title="Volunteer map after the Bogot&aacute; earthquake",
        desc="A live dashboard of volunteer and donation points after the Bogotá earthquake.",
        figures=[("media/voluntariado-1.jpg", "What the page shows today: a notice pointing to the coordinators' own site.")],
        details=[
            ("Year", "2026"),
            ("Role", "Design and code"),
            ("Stack", "Next.js, Vercel, Google Sheets"),
            ("Visit", link("https://voluntariado-colombia.vercel.app/", "Site") + " &middot; " + link("https://github.com/everandres/voluntariado-colombia", "Repository")),
        ],
        left=[
            "After the earthquake, people coordinated volunteer and donation points in one shared Google Sheet that many people edited at the same time. I built a live dashboard on top of it, so anyone could find where help was needed without touching the sheet.",
            "The hard part was the data: columns and headers kept changing as people edited, so the site recognizes columns by a catalogue of names instead of fixed positions, and a legend explains what each status label means.",
        ],
        right=[
            "When the coordinators moved all the points to their own collection site and emptied the sheet, I replaced the map with a notice that sends people to redacopiobogota.com. That is what the page shows today.",
        ],
    ),
}

# Small factual fixes to the 2023 project pages, applied to their original content.
LEGACY_FIXES = {
    2: [("October 2019 - Present", "2020 &ndash; June 2024"),
        ("<a>Cofunder</a>", "<a>Co-founder &amp; Academic Director</a>"),
        ("I'm the co-founder of Orbis Geoscripting, where we've spent the last three years teaching",
         "I co-founded Orbis Geoscripting, where between 2020 and 2024 we taught")],
    4: [("November 2019 - Present", "Since 2019")],
}


def legacy_inner(n):
    # Always read the original 2023 page (commit 836fc7d) so the build can be re-run.
    html = subprocess.run(["git", "show", f"836fc7d:portfolio-single-{n}.html"], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout
    m = re.search(r'<div class="portfolio-single-inner">(.*?)\n\s*</div>\s*</div>\s*</div>\s*</div>\s*\n\s*<div class="site-footer">', html, re.S)
    if not m:
        raise SystemExit(f"could not find content of portfolio-single-{n}.html")
    inner = m.group(1)
    for old, new in LEGACY_FIXES.get(n, []):
        if old not in inner:
            raise SystemExit(f"fix not found in page {n}: {old!r}")
        inner = inner.replace(old, new)
    title = re.search(r'heading-portfolio-single-h2[^>]*>(.*?)</h2>', inner).group(1)
    return title, inner


def write(n, title, desc, inner):
    out = HEAD.format(title=re.sub("<[^>]+>", "", title), desc=desc) + inner + TAIL.format(footer=FOOTER)
    (ROOT / f"portfolio-single-{n}.html").write_text(out, encoding="utf-8")


if __name__ == "__main__":
    legacy = {n: legacy_inner(n) for n in (1, 2, 3, 4)}  # read before anything is rewritten
    for n, (title, inner) in legacy.items():
        write(n, title, "Ever Andrés Salazar Mercado, portfolio.", inner)
    for n, p in PAGES.items():
        write(n, p["title"], p["desc"], body(p))
    print("pages:", sorted(list(legacy) + list(PAGES)))
