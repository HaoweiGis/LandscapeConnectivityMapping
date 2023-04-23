using Omniscape

land_cover, wkt, transform = Omniscape.read_raster("lc2_china300_remspa_32649.tif", Float64)

reclass_table = [
    1.	1;
    2	5;
    3	10;
    4	15;
    5	20;
    6	30;
    7	25;
    8	35;
    9	20;
    10	30;
    11	35;
    12	25;
    13	40;
    14	500;
    15	300;
    16	200;
    17	missing;
]

config = Dict{String, String}(
    "radius" => "100",
    "block_size" => "21",
    "project_name" => "md_mspa_omniscape_output_new",
    "source_from_resistance" => "true",
    "reclassify_resistance" => "true",
    "calc_normalized_current" => "true",
    "calc_flow_potential" => "true"
)

currmap, flow_pot, norm_current = run_omniscape(config,
                                                land_cover,
                                                reclass_table = reclass_table,
                                                wkt = wkt,
                                                geotransform = transform,
                                                write_outputs = true)