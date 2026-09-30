"""Inject real PowerPoint animations + Morph transitions into deck_raw.pptx.

pptxgenjs cannot write <p:timing>/<p:transition>, so we add them to each
slide XML. Every effect auto-plays (After/With Previous) in a purposeful
order; nothing bounces. Shapes are addressed by their objectName.
"""
import re, zipfile, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "deck_raw.pptx")
DST = os.path.join(HERE, "Forgetting_Curve_Premium_4_Slides.pptx")

# (names, effect, delay ms, duration ms)
#   fade | appear | zoom (fade+scale) | wipeL / wipeR | path:<svg path>
PLAN = {
    1: [
        (["!!orb"], "fade", 0, 1200),
        (["!!orb"], "path:M 0 0 C 0.02 -0.015 0.04 -0.02 0.05 -0.03 E", 0, 9000),
        (["hook_kicker"], "fade", 300, 500),
        (["hook_stat"], "zoom", 600, 700),
        (["hook_line"], "wipeR", 1300, 700),
        (["hook_curve"], "wipeL", 1900, 1800),
        (["hook_axis_start", "hook_axis_end"], "fade", 3500, 500),
        (["hook_title"], "fade", 3000, 700),
        (["hook_subtitle"], "fade", 3350, 600),
        (["hook_source"], "fade", 3900, 500),
    ],
    2: [
        (["c_title"], "fade", 0, 600),
        (["c_sub"], "fade", 250, 500),
        (["c_chart_card"], "fade", 500, 500),
        (["c_chart"], "wipeL", 800, 1600),
        *[([f"c_card{k}_bg", f"c_card{k}_dot", f"c_card{k}_icon", f"c_card{k}_title", f"c_card{k}_body"],
            "fade", 2300 + (k - 1) * 450, 500) for k in (1, 2, 3)],
    ],
    3: [
        (["e_title"], "fade", 0, 600),
        (["e_sub"], "fade", 250, 500),
        (["e_chart_card"], "fade", 500, 500),
        (["e_leg_amber", "e_leg_amber_t", "e_leg_teal", "e_leg_teal_t", "e_axis_x", "e_axis_y"], "fade", 700, 500),
        (["e_chart"], "wipeL", 1000, 2200),
        (["e_note"], "appear", 3000, 1),
        (["e_before_bg", "e_before_dot", "e_before_icon", "e_before_label", "e_before_caption"], "fade", 3200, 500),
        (["e_before_value"], "zoom", 3400, 500),
        (["e_after_bg", "e_after_dot", "e_after_icon", "e_after_label", "e_after_caption"], "fade", 3900, 500),
        (["e_after_value"], "zoom", 4100, 600),
    ],
    4: [
        (["k_kicker"], "fade", 0, 500),
        (["k_title"], "zoom", 250, 700),
        # day badges appear one by one, right to left, links wipe towards the next
        *[x for k in (1, 2, 3, 4) for x in (
            ([f"k_day{k}", f"k_day{k}_n", f"k_day{k}_u"], "zoom", 1000 + (k - 1) * 550, 450),
            ([f"k_day{k}_l"], "fade", 1150 + (k - 1) * 550, 400),
        )],
        *[([f"k_link{k}"], "wipeR", 1350 + (k - 1) * 550, 350) for k in (1, 2, 3)],
        (["k_quote"], "fade", 3400, 900),
        *[([f"k_tip{k}_bg", f"k_tip{k}_dot", f"k_tip{k}_icon", f"k_tip{k}_title", f"k_tip{k}_body"],
            "fade", 4400 + (k - 1) * 350, 500) for k in (1, 2, 3)],
        (["!!orb"], "path:M 0 0 C 0 0.01 0 0.02 0 0.025 E", 0, 8000),
    ],
}

TRANSITION = (
    '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
    '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">'
    '<p:transition spd="slow"><p159:morph option="byObject"/></p:transition></mc:Choice>'
    '<mc:Fallback><p:transition spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>'
)


class Ids:
    def __init__(self): self.n = 2
    def __call__(self): self.n += 1; return self.n


def tgt(spid): return f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'


def set_visible(nid, spid):
    return (f'<p:set><p:cBhvr><p:cTn id="{nid()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'{tgt(spid)}<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:to><p:strVal val="visible"/></p:to></p:set>')


def filt(nid, spid, f, dur):
    return (f'<p:animEffect transition="in" filter="{f}"><p:cBhvr><p:cTn id="{nid()}" dur="{dur}"/>{tgt(spid)}</p:cBhvr></p:animEffect>')


def scale(nid, spid, attr, dur):
    return (f'<p:anim calcmode="lin" valueType="num"><p:cBhvr><p:cTn id="{nid()}" dur="{dur}" decel="100000" fill="hold"/>{tgt(spid)}'
            f'<p:attrNameLst><p:attrName>{attr}</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst>'
            f'<p:tav tm="0"><p:val><p:strVal val="#{attr}*0.85"/></p:val></p:tav>'
            f'<p:tav tm="100000"><p:val><p:strVal val="#{attr}"/></p:val></p:tav></p:tavLst></p:anim>')


def effect(nid, spid, kind, delay, dur, node, grp):
    head = lambda pid, cls, sub, extra="": (
        f'<p:par><p:cTn id="{nid()}" presetID="{pid}" presetClass="{cls}" presetSubtype="{sub}" fill="hold"{grp}{extra} '
        f'nodeType="{node}"><p:stCondLst><p:cond delay="{delay}"/></p:stCondLst><p:childTnLst>')
    tail = '</p:childTnLst></p:cTn></p:par>'
    if kind == "fade":
        return head(10, "entr", 0) + set_visible(nid, spid) + filt(nid, spid, "fade", dur) + tail
    if kind == "appear":
        return head(1, "entr", 0) + set_visible(nid, spid) + tail
    if kind == "zoom":  # "Fade Zoom" - subtle 85% -> 100% with fade, decelerated
        return (head(53, "entr", 16) + set_visible(nid, spid) + scale(nid, spid, "ppt_w", dur)
                + scale(nid, spid, "ppt_h", dur) + filt(nid, spid, "fade", dur) + tail)
    if kind in ("wipeL", "wipeR"):
        sub, f = (8, "wipe(left)") if kind == "wipeL" else (2, "wipe(right)")
        return head(22, "entr", sub) + set_visible(nid, spid) + filt(nid, spid, f, dur) + tail
    if kind.startswith("path:"):
        path = kind[5:]
        return (head(0, "path", 0, ' accel="50000" decel="50000"')
                + f'<p:animMotion origin="layout" path="{path}" pathEditMode="relative" ptsTypes="">'
                f'<p:cBhvr><p:cTn id="{nid()}" dur="{dur}" fill="hold"/>{tgt(spid)}'
                '<p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr>'
                '<p:rCtr x="0" y="0"/></p:animMotion>' + tail)
    raise ValueError(kind)


def build_timing(xml, plan):
    shapes = dict((n, (int(i), tag)) for tag, i, n in re.findall(
        r'<p:(sp|pic|graphicFrame|cxnSp)>\s*<p:nv\w+>\s*<p:cNvPr id="(\d+)" name="([^"]*)"', xml))
    nid = Ids()
    items, bld, first = [], {}, True
    for names, kind, delay, dur in sorted(plan, key=lambda p: p[2]):
        for name in names:
            if name not in shapes:
                sys.exit(f"missing shape {name}")
            spid, tag = shapes[name]
            is_entr = not kind.startswith("path:")
            grp = ' grpId="0"' if is_entr else ' grpId="1"'
            items.append(effect(nid, spid, kind, delay, dur, "afterEffect" if first else "withEffect", grp))
            first = False
            if tag == "sp":
                bld.setdefault(spid, f'<p:bldP spid="{spid}" grpId="0" animBg="1"/>')
            elif tag == "graphicFrame":
                bld.setdefault(spid, f'<p:bldGraphic spid="{spid}" grpId="0"><p:bldAsOne/></p:bldGraphic>')
    return ('<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
            '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
            f'<p:par><p:cTn id="{nid()}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>'
            '<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
            f'<p:par><p:cTn id="{nid()}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
            + "".join(items) +
            '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
            '</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
            '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
            '</p:childTnLst></p:cTn></p:par></p:tnLst>'
            + (f'<p:bldLst>{"".join(bld.values())}</p:bldLst>' if bld else "") + '</p:timing>')


zin = zipfile.ZipFile(SRC)
zout = zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    data = zin.read(item.filename)
    m = re.fullmatch(r"ppt/slides/slide(\d+)\.xml", item.filename)
    if m:
        xml = data.decode("utf-8")
        assert "<p:timing" not in xml and "<p:transition" not in xml
        xml = xml.replace("</p:clrMapOvr>", "</p:clrMapOvr>" + TRANSITION + build_timing(xml, PLAN[int(m.group(1))]), 1)
        data = xml.encode("utf-8")
    zout.writestr(item, data)
zout.close()
print("wrote", DST)
