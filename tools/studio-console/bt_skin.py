import bt_img as I
AMBH = "FFB038"; DIMH = "C07C20"; CREAMH = "D2CEBC"; SELH = "F2FFF4"; UNSELH = "DCE6E0"
NAMEMAP = [("Recent Bookmarks", 1), ("Files", 2), ("Database", 3), ("Resume Playback", 4), ("Now Playing", 4), ("Settings", 5), ("Playlists", 6), ("Bluetooth", 7), ("Plugins", 8), ("System", 9), ("Shortcuts", 10)]
def chain(label):
    s = "".join(f"%?if(%LT,=,{n})<%xd({label},{k})|" for n, k in NAMEMAP)
    return s + f"%xd({label},%LN)" + ">" * len(NAMEMAP)
def sbs(NAME, ID):
    gx, gy = I.CELLX, I.CELLY
    return f"""# {NAME} - base skin (menus, lists, USB) for HiBy R1, 480x800.
# Main menu = 2-column grid of smoked pads that glow green when selected (up to 5 rows = 10 root-menu items);
# every other list = one-column rows with the same glowing pad.  All static art is baked into bg_menu.bmp; the only live graphics
# are the pad / row sprites, the icon sprites, the header battery bars, the scroll thumb and the footer progress fill.
%X(bg_menu.bmp)
%Fl(2,{ID}-16.fnt)
%Fl(3,{ID}-24.fnt)
%Fl(4,{ID}-32.fnt)

%xl(pad,pad.bmp,0,0,2)
%xl(ic,ic.bmp,0,0,11)
%xl(ics,ics.bmp,0,0,11)
%xl(rowim,rows.bmp,0,0,2)
%xl(thmb,thumb.bmp,0,0)
%xl(hbat,hbat.bmp,0,0)
%xl(pbf,pbf.bmp,0,0)

%Vi(tiles,{gx},{gy},452,620,2)
%Vi(ui_usb,0,152,2,2,2)
%?if(%cs,=,21)<%VI(ui_usb)|%VI(tiles)%?if(%Lt,=,Rockbox)<%Lb(it,226,124,tile)|%Lb(rw,452,76)>>

%?if(%cs,=,21)<%Vd(ut)%Vd(ub)|%?Lt<%Vd(ht)>>
# bar viewports must be switched on from this always-visible viewport (a hidden viewport can never enable itself)
%?mp<%Vd(bid)|%Vd(btl)%Vd(bar)%Vd(btm)%Vd(bpb)%Vd(btt)|%Vd(btl)%Vd(bar)%Vd(btm)%Vd(bpb)%Vd(btt)|%Vd(btl)%Vd(bar)%Vd(btm)%Vd(bpb)%Vd(btt)|%Vd(btl)%Vd(bar)%Vd(btm)%Vd(bpb)%Vd(btt)>

# ---- clear the whole screen to the backdrop ----
%V(0,0,480,800,-)

# ---- header LCD: title | clock | battery bars + % ----
%Vl(ht,24,21,232,24,3)%Vf({AMBH})
%s%al%Lt

%V(272,21,84,24,3)%Vf({AMBH})
%al%cH:%cM

# 10 baked dim bars; the lit copy is clipped to the battery level
%V(366,22,36,22,-)
%bl(0,0,36,22,hbat)

%V(404,21,56,24,3)%Vf({AMBH})
%al%bl%%

# ---- footer: song LCD + elapsed readout + position strip (only while something is loaded: play / pause / seeking) ----
# tap anywhere on the footer -> back to the playback screen.  This viewport is cleared when it appears, so it MUST come before
# the text viewports
%Vl(btt,0,700,480,100,-)
%T(open,0,0,-,-,resumeplayback)

%Vl(bid,32,728,296,16,2)%Vf({DIMH})
%alNOTHING PLAYING

%Vl(btl,32,717,300,24,3)%Vf({AMBH})
%s%al%?it<%it|%fn>

%Vl(bar,32,741,300,16,2)%Vf({DIMH})
%s%al%?ia<%ia|>

%Vl(btm,358,718,94,24,3)%Vf({AMBH})
%ar%pc

%Vl(bpb,20,770,440,7,-)
%pb(0,0,-,7,pbf,notouch)

# ---- USB screen ----
%Vl(ut,32,100,416,24,3)%Vf({AMBH})
%alUSB connected

%Vl(ub,20,200,440,160,3)%Vf({CREAMH})
%acYour player is connected
%acto a computer.
%ac
%acEject it there before
%acunplugging the cable.

# ---- list scroll thumb (row lists) ----
%V(450,80,14,600,-)
%?if(%Lt,=,Rockbox)<|%?LB<%LB(0,0,14,600,invert,nobar,slider,thmb,notouch)>>

# ====================== list item viewports ======================
# ---- main-menu tile (cell 226x124): layer 1 = pad (glows when selected) ----
%Vl(it,0,0,226,124,-)
%?Lc<%xd(pad,2)|%xd(pad,1)>

# layer 2 = icon picked from the item's name (other languages fall back to the item's position in the default menu order)
%Vl(it,83,19,60,56,-)
%?Lc<{chain('ics')}|{chain('ic')}>

# layer 3 = caption
%Vl(it,13,87,200,24,3)%Vf({UNSELH})
%ac%LT

# ---- row list item (cell 452x76) ----
%Vl(rw,0,0,452,76,-)
%?Lc<%xd(rowim,2)|%xd(rowim,1)>
%Vl(rw,26,22,370,32,4)%Vf({UNSELH})
%s%al%LT
"""
def wps(NAME, ID):
    cx, cy, cw, ch = I.seg_rect("clock"); ex, ey, ew, eh = I.seg_rect("elap"); rx, ry, rw_, rh = I.seg_rect("rem"); bx, by, bw, bh = I.seg_rect("batt")
    return f"""# {NAME} - playback screen (480x800 portrait): a vintage recording-console panel.
#   art + live L/R LED peak meters + vertical touch volume fader / song display with battery gauge / info plates + clock /
#   elapsed + remain readouts over the position fader / transport keys, shuffle + repeat, menu knob.
# Touch buttons need Settings > General Settings > Display > Touchscreen Settings > Touchscreen mode > Point.
%wd
%X(bg_wps.bmp)
%Fl(2,{ID}-16.fnt)
%Fl(3,{ID}-24.fnt)
%Fl(4,{ID}-32.fnt)
%Fl(5,{ID}-s20.fnt)
%Fl(6,{ID}-s14.fnt)
%Fl(7,{ID}-s13.fnt)

%xl(ml,ml.bmp,0,0)
%xl(vk,vk.bmp,0,0)
%xl(hk,hk.bmp,0,0)
%xl(bfl,bf.bmp,0,0)
%xl(ppi,pp.bmp,0,0,2)
%xl(shi,sh.bmp,0,0,2)
%xl(rpi,rp.bmp,0,0,5)
%xl(lmp,lp.bmp,0,0,2)

# ---- clear the whole screen to the backdrop ----
%V(0,0,480,800,-)

# ---- album art (the no-cover placeholder is baked into the backdrop) ----
%V(26,28,220,220,1)
%Cl(0,0,220,220,c,c)
%?C<%Cd>

# ---- live L / R peak meters: the lit LED ladder is clipped to the audio level over the baked dim ladder ----
%V(274,98,36,294,-)
%pL(0,0,36,294,ml)
%V(318,98,36,294,-)
%pR(0,0,36,294,ml)

# ---- vertical volume fader: drag the cap (bar taller than wide = vertical, the volume bar makes its own touch area) ----
%V(395,95,44,294,-)
%pv(0,0,44,294,nobar,slider,vk)
%V(366,396,102,16,2)%Vf({AMBH})
%ac%pv dB

# ---- song display ----
%V(26,278,224,32,4)%Vf({AMBH})
%s%al%?it<%it|%fn>
%V(26,322,224,24,3)%Vf({DIMH})
%s%al%?ia<%ia|Unknown Artist>
%V(26,352,224,16,2)%Vf({DIMH})
%s%al%?id<%id|Unknown Album>

# ---- battery gauge: dim bars are baked, the lit ones are clipped to the level; digits are a 7-segment readout ----
%V(376,22,82,12,-)
%bl(0,0,82,12,bfl)
%V({bx},{by},{bw},{bh},7)%Vf({AMBH})
%ar%bl

# ---- info plates: format | bitrate | track n/N, then the clock ----
%V(12,400,62,16,2)%Vf({CREAMH})
%ac%fc
%V(79,400,70,16,2)%Vf({CREAMH})
%ac%fbk
%V(154,400,106,16,2)%Vf({CREAMH})
%ac%pp/%pe
%V({cx},{cy},{cw},{ch},5)%Vf({AMBH})
%al%cH:%cM

# ---- position bay: elapsed / remain readouts ----
%V({ex},{ey},{ew},{eh},6)%Vf({AMBH})
%ar%pc
%V({rx},{ry},{rw_},{rh},6)%Vf({AMBH})
%ar%pr

# ---- position fader: touch band first, then the bar (cap moves along the slot) ----
%V(10,468,460,56,-)
%T(seek,0,0,-,-,progressbar)
%V(19,475,442,42,-)
%pb(0,0,442,42,nobar,slider,hk,notouch)

# ---- transport ----
%V(20,550,88,124,-)
%T(prev,0,0,-,-,wps_prev)
%V(108,550,85,124,-)
%T(rew,0,0,-,-,rwd,repeat_press)
%V(193,550,94,124,-)
%T(play,0,0,-,-,play)
%T(stop,0,0,-,-,stop,long_press)
%V(287,550,84,124,-)
%T(ff,0,0,-,-,ffwd,repeat_press)
%V(371,550,89,124,-)
%T(next,0,0,-,-,wps_next)

# play lamp: lit while playing (also while winding), off when stopped or paused
%V(231,536,18,14,-)
%?mp<%xd(lmp,1)|%xd(lmp,2)|%xd(lmp,1)|%xd(lmp,2)|%xd(lmp,2)>

# play / pause glyph on the red key
%V(216,590,48,44,-)
%?mp<%xd(ppi,1)|%xd(ppi,2)|%xd(ppi,1)|%xd(ppi,1)|%xd(ppi,1)>

# ---- shuffle / repeat keys (the whole key is a sprite: glyph + lamp) ----
%V(30,712,70,46,-)
%T(shuf,0,0,-,-,shuffle)
%?ps<%xd(shi,2)|%xd(shi,1)>
%V(180,712,70,46,-)
%T(mode,0,0,-,-,repmode)
%?mm<%xd(rpi,1)|%xd(rpi,2)|%xd(rpi,3)|%xd(rpi,4)|%xd(rpi,5)>

# ---- MENU knob -> context menu ----
%V(372,700,64,64,-)
%T(menu,0,0,-,-,contextmenu)
"""
def cfg(NAME, ID):
    return f"""# Theme:        {NAME}
# Author:       Oddlogic
# Source:       https://github.com/oddlogic-space/oddlogic-rockbox-themes  (latest version, changelog, bug reports)
# Platform:     HiBy R1 (480x800 portrait touch), Rockbox hosted build
# Version:      1.1
# License:      CC-BY-SA 4.0 (skins and graphics). Fonts: Noto Sans CJK (SIL OFL 1.1), GNU Unifont (SIL OFL 1.1 / GPL with font exception), DSEG7 (SIL OFL 1.1), see fonts/COPYING-{ID}.txt
# Graphics:     all original (backdrops, pads, icons, keys and meters drawn by the author for this theme)
# Updated:      2026-10-14
#
# Vintage recording-console playback screen (LED peak meters, touch volume fader, transport keys) with smoked glowing pad menus.
# IMPORTANT: touch buttons need  Settings > General Settings > Display >
#   Touchscreen Settings > Touchscreen mode > Point
wps: /.rockbox/wps/{ID}.wps
sbs: /.rockbox/wps/{ID}.sbs
font: /.rockbox/fonts/{ID}-24.fnt
backdrop: -
show icons: off
filetype colours: -
statusbar: top
scrollbar: off
foreground color: FFB038
background color: 0E0F0E
line selector start color: 123A1C
line selector end color: 123A1C
line selector text color: F2FFF4
selector type: bar (gradient)
ui viewport: -
list padding: 14
"""
