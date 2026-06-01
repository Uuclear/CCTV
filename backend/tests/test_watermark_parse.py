"""watermark_parse — docs/design/watermark-ocr-extraction.md §10."""

from app.services.watermark_parse import (
    infer_pipe_system,
    parse_chain_from_text,
    parse_from_text_blocks,
    score_material,
)


def test_chain_w9_w9_1():
    cp = parse_chain_from_text("W9-W9-1")
    assert cp.start == "W9"
    assert cp.end == "W9-1"
    assert cp.mode == "well_pair"


def test_chain_descriptive_end():
    cp = parse_chain_from_text("w9-污水监测井")
    assert cp.start == "W9"
    assert cp.end == "污水监测井"
    assert cp.mode == "descriptive_end"


def test_chain_w9_1_w9_2():
    cp = parse_chain_from_text("W9-1-W9-2")
    assert cp.start == "W9-1"
    assert cp.end == "W9-2"


def test_chain_road_well_nh2w5():
    cp = parse_chain_from_text("w11-2-nh2w-5")
    assert cp.start == "W11-2"
    assert cp.end == "NH2W-5"
    assert cp.mode == "well_pair"


def test_chain_road_well_ocr_nhw5():
    cp = parse_chain_from_text("w11-2-nhw-5")
    assert cp.start == "W11-2"
    assert cp.end == "NH2W-5"
    assert cp.mode == "well_pair"


def test_infer_pipe_system():
    assert infer_pipe_system("W9", "W10", "w9-w10") == "污水"
    assert infer_pipe_system("Y9", "Y10", "") == "雨水"
    assert infer_pipe_system("H11", "H12", "") == "合流"


def test_material_pipe_suffix():
    sc, mat = score_material("球墨铸铁管")
    assert sc >= 0.9
    assert mat == "球墨铸铁"
    sc2, mat2 = score_material("球墨铸铁")
    assert sc2 >= 0.85 and mat2 == "球墨铸铁"
    sc3, mat3 = score_material("HDPE管")
    assert mat3 == "HDPE"
    sc4, mat4 = score_material("混凝土管")
    assert mat4 == "混凝土"


def test_material_ends_with_guan_only():
    sc, mat = score_material("塑料管")
    assert sc >= 0.85 and mat == "塑料"


def test_shuffled_blocks_t8():
    blocks = ["球墨铸铁管", "DN500", "w9-w10"]
    r = parse_from_text_blocks(blocks, "")
    assert r.chain_start_label == "W9"
    assert r.chain_end_label == "W10"
    assert r.diameter_mm == 500
    assert r.pipe_material == "球墨铸铁"
    assert r.pipe_system == "污水"


def test_shuffled_blocks_t9():
    blocks = ["DN500", "w9-w10", "球墨铸铁管"]
    r = parse_from_text_blocks(blocks, "")
    assert r.chain_start_label == "W9"
    assert r.chain_end_label == "W10"
    assert r.diameter_mm == 500
    assert r.pipe_material == "球墨铸铁"


def test_date_block():
    r = parse_from_text_blocks(["2026/4/21"], "")
    assert r.inspection_date == "2026-04-21"


def test_filename_w11_descriptive():
    r = parse_from_text_blocks([], "W11-污水监测井")
    assert r.chain_start_label == "W11"
    assert r.chain_end_label == "污水监测井"
