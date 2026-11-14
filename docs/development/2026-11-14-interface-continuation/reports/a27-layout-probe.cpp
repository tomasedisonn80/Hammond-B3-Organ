// A27 read-only ordinary-control exporter. This is not a CTest target.
// See session27-responsive-inventory.md for the exact build/run command.
// Geometry/hit decisions come from UiModel; rectangle comparisons are performed
// separately by a27-analyze-layout.py. Font envelopes use the embedded atlas and
// the inspected centered-text fitting rule, not raster/physical-DPI measurement.
#include "UiModel.h"
#include "FontData.h"

#include <algorithm>
#include <array>
#include <iomanip>
#include <iostream>
#include <limits>
#include <string>
#include <string_view>

using namespace hammond;
using namespace hammond::standalone;

namespace {
void rect(UiRect r) {
    std::cout << '[' << r.x << ',' << r.y << ',' << r.width << ',' << r.height << ']';
}
void id(UiControlId c) {
    std::cout << '[' << static_cast<unsigned>(c.kind) << ',' << static_cast<unsigned>(c.manual)
              << ',' << static_cast<unsigned>(c.bank) << ',' << static_cast<unsigned>(c.index) << ']';
}
UiRect inset(UiRect r, float d) { return {r.x+d,r.y+d,r.width-2*d,r.height-2*d}; }
bool sharp(unsigned i) { return i==1 || i==3 || i==6 || i==8 || i==10; }
bool common(UiControlKind k) {
    return k==UiControlKind::Workspace || k==UiControlKind::Presentation ||
        k==UiControlKind::SaveControls || k==UiControlKind::LoadControls ||
        k==UiControlKind::Help || k==UiControlKind::AudioSettings ||
        k==UiControlKind::MidiSettings || k==UiControlKind::Panic;
}
std::string_view label(UiControlId c) {
    switch(c.kind) {
    case UiControlKind::EditBank: return c.bank==DrawbarBank::A ? "EDIT A" : "EDIT B";
    case UiControlKind::KeyboardTarget: return c.index==0 ? "UPPER" : c.index==1 ? "LOWER" : "PEDALS";
    case UiControlKind::OctaveDown: return "OCT -";
    case UiControlKind::OctaveUp: return "OCT +";
    case UiControlKind::SaveControls: return "SAVE";
    case UiControlKind::LoadControls: return "LOAD";
    case UiControlKind::Help: return "HELP";
    case UiControlKind::AudioSettings: return "AUDIO";
    case UiControlKind::MidiSettings: return "MIDI";
    case UiControlKind::Panic: return "PANIC";
    case UiControlKind::Workspace: return c.index==0 ? "PLAY" : c.index==1 ? "ROTARY" : "SERVICE";
    case UiControlKind::Presentation: return "FLAT";
    default: return "";
    }
}
UiRect parent(const UiLayout& l, UiControlId c) {
    if(common(c.kind)) return l.header;
    const auto m=static_cast<std::size_t>(c.manual);
    if(c.kind==UiControlKind::PresetKey) return l.preset_key_panels[m];
    if(c.kind==UiControlKind::ManualDrawbar) return l.registration_panels[m];
    if(c.kind==UiControlKind::EditBank)
        return l.bank_controls_in_cheeks ? l.manual_rail_panels[m] : l.registration_panels[m];
    if(c.kind==UiControlKind::KeyboardTarget || c.kind==UiControlKind::OctaveDown || c.kind==UiControlKind::OctaveUp)
        return l.keyboard_toolbar;
    return l.performance_panel;
}
float advance(std::string_view s, float size, const font_data::Atlas& atlas) {
    float total=0;
    for(char c:s) total+=static_cast<float>(font_data::glyph(atlas,static_cast<unsigned char>(c)).advance_64)
        * (size/static_cast<float>(atlas.pixel_height))/64.0F;
    return total;
}
void text_sample(std::string_view role,std::string_view s,UiRect b,float requested,bool serif=false,float padding=3) {
    const auto& atlas=serif ? font_data::kSerif : font_data::kSans;
    float size=std::min(requested,b.height/1.2F);
    const float first=advance(s,size,atlas);
    if(first>b.width-2*padding && first>0) size*=std::max(0.1F,b.width-2*padding)/first;
    const float width=advance(s,size,atlas), scale=size/static_cast<float>(atlas.pixel_height);
    float x=b.x+(b.width-width)/2;
    const float top=b.y+(b.height-size*1.2F)/2;
    const float baseline=top+static_cast<float>(atlas.ascent)*scale;
    float left=std::numeric_limits<float>::max(),right=-left,up=left,down=-left;
    for(char c:s) {
        const auto& g=font_data::glyph(atlas,static_cast<unsigned char>(c));
        if(g.width && g.height) {
            const float gx=x+static_cast<float>(g.bearing_x)*scale;
            const float gy=baseline+static_cast<float>(g.bearing_y)*scale;
            left=std::min(left,gx);right=std::max(right,gx+static_cast<float>(g.width)*scale);
            up=std::min(up,gy);down=std::max(down,gy+static_cast<float>(g.height)*scale);
        }
        x+=static_cast<float>(g.advance_64)*scale/64;
    }
    std::cout << "{\"role\":" << std::quoted(std::string(role)) << ",\"text\":" << std::quoted(std::string(s))
              << ",\"requested_size\":" << requested << ",\"effective_size\":" << size
              << ",\"advance\":" << width << ",\"box\":";
    rect(b);std::cout << ",\"ink_envelope\":";rect({left,up,right-left,down-up});std::cout << '}';
}
void control_text(const UiControlGeometry& c,bool flat) {
    std::cout << '[';
    switch(c.id.kind) {
    case UiControlKind::ManualDrawbar:
        text_sample("label",kUiFootageLabels[c.id.index],c.label_bounds,13,true);std::cout << ',';
        text_sample("value","8",c.value_bounds,13);break;
    case UiControlKind::PedalDrawbar:
        text_sample("label",c.id.index==0 ? "MIX 1" : "MIX 2",c.label_bounds,11);std::cout << ',';
        text_sample("value","8",c.value_bounds,13);break;
    case UiControlKind::Expression:
        text_sample("label","NOMINAL EXPRESSION",c.label_bounds,10.5F);std::cout << ',';
        text_sample("value","100%",c.value_bounds,11.5F);break;
    case UiControlKind::Percussion: {
        constexpr std::array<std::string_view,4> labels{"PERC","HARMONIC","VOLUME","DECAY"};
        constexpr std::array<std::string_view,4> first{"ON","2ND","NORM","SLOW"};
        constexpr std::array<std::string_view,4> second{"OFF","3RD","SOFT","FAST"};
        text_sample("label",labels[c.id.index],c.label_bounds,10);std::cout << ',';
        text_sample("value",first[c.id.index],c.value_bounds,14,true);std::cout << ',';
        text_sample("alternate_value",second[c.id.index],c.value_bounds,14,true);break;
    }
    case UiControlKind::PresetKey: {
        constexpr std::array<std::string_view,12> labels{"C","C#","D","D#","E","F","F#","G","G#","A","A#","B"};
        text_sample("label",labels[c.id.index],c.label_bounds,9,false,0);break;
    }
    default:
        text_sample("label",label(c.id),inset(c.bounds,flat ? 3.0F : 4.0F),
                    flat ? 11.0F : common(c.id.kind) ? 15.0F : 11.0F,
                    !flat && common(c.id.kind));break;
    }
    std::cout << ']';
}
void probe_point(const UiLayout& l,UiPoint p) {
    std::cout << "{\"point\":[" << p.x << ',' << p.y << "],\"hit\":";
    id(ui_hit_test(l,p));std::cout << '}';
}
void probe_rect(const UiLayout& l,UiRect r) {
    std::cout << '[';
    const float e=std::min({0.25F,r.width/4,r.height/4});
    const std::array<UiPoint,5> points{{{r.x+r.width/2,r.y+r.height/2},
        {r.x+e,r.y+e},{r.x+r.width-e,r.y+e},{r.x+e,r.y+r.height-e},{r.x+r.width-e,r.y+r.height-e}}};
    for(std::size_t i=0;i<points.size();++i) { if(i) std::cout << ',';probe_point(l,points[i]); }
    std::cout << ']';
}
void paint_rects(const UiControlGeometry& c) {
    const auto t=c.track;
    std::cout << '[';
    if(c.id.kind==UiControlKind::ManualDrawbar || c.id.kind==UiControlKind::PedalDrawbar) {
        const float w=std::max(10.0F,std::min(34.0F,c.bounds.width-8));
        const float h=c.id.kind==UiControlKind::PedalDrawbar ? 22.0F : 26.0F;
        const float sw=std::min(c.bounds.width-2,w+8), x=t.x+t.width/2;
        rect({x-sw/2,t.y-h/2,sw,t.height+h});std::cout << ',';
        rect({x-w/2,t.y-h/2,w,h});std::cout << ',';rect({x-w/2,t.y+t.height-h/2,w,h});
    } else if(c.id.kind==UiControlKind::Expression) {
        rect({t.x-3,t.y-5,t.width+6,10});std::cout << ',';
        rect({t.x-7,t.y-11,14,22});std::cout << ',';rect({t.x+t.width-7,t.y-11,14,22});
    }
    std::cout << ']';
}
} // namespace

int main() {
    std::cout << std::setprecision(9) << "{\"cases\":[";
    constexpr std::array<std::array<float,2>,9> sizes{{{960,700},{1280,900},{1672,941},
        {1399,819},{1399,820},{1400,819},{1400,820},{8192,700},{960,8192}}};
    bool first_case=true;
    for(const auto wh:sizes) for(unsigned w=0;w<3;++w) for(unsigned p=0;p<2;++p) {
        UiLayout l;
        if(!make_ui_layout(wh[0],wh[1],{DrawbarBank::A,DrawbarBank::B},l,
            static_cast<UiWorkspace>(w),static_cast<UiPresentation>(p))) return 2;
        if(!first_case) std::cout << ',';
        first_case=false;
        std::cout << "{\"size\":[" << wh[0] << ',' << wh[1] << "],\"workspace\":" << w
                  << ",\"presentation\":" << p << ",\"retained_controls\":" << l.control_count
                  << ",\"cabinet\":" << l.show_cabinet << ",\"edit_in_cheeks\":" << l.bank_controls_in_cheeks
                  << ",\"workspace_panel\":";rect(l.workspace_panel);
        std::cout << ",\"panels\":[";
        const std::array<UiRect,12> panels{l.header,l.performance_panel,l.registration_panels[0],l.registration_panels[1],
            l.keyboard_toolbar,l.manual_rail_panels[0],l.manual_panels[0],l.manual_rail_panels[1],l.manual_panels[1],
            l.pedal_panel,l.footer,l.cabinet_panel};
        for(std::size_t i=0;i<panels.size();++i) {if(i)std::cout<<',';rect(panels[i]);}
        std::cout << "],\"controls\":[";bool first_control=true;
        for(std::size_t i=0;i<l.control_count;++i) {
            const auto& c=l.controls[i];if(!ui_control_visible(l,c.id)) continue;
            if(!first_control)std::cout<<',';
            first_control=false;
            std::cout << "{\"ordinal\":" << i << ",\"id\":";id(c.id);
            std::cout << ",\"bounds\":";rect(c.bounds);std::cout << ",\"label\":";rect(c.label_bounds);
            std::cout << ",\"value\":";rect(c.value_bounds);std::cout << ",\"track\":";rect(c.track);
            std::cout << ",\"parent\":";rect(parent(l,c.id));
            UiRect exposed=c.bounds;
            if(c.id.kind==UiControlKind::PresetKey && !sharp(c.id.index))
                exposed={c.bounds.x,c.bounds.y+c.bounds.height*0.62F,c.bounds.width,c.bounds.height*0.38F};
            std::cout << ",\"exposed\":";rect(exposed);
            std::cout << ",\"pointer_samples\":";probe_rect(l,exposed);
            std::cout << ",\"label_center\":";probe_point(l,{c.label_bounds.x+c.label_bounds.width/2,c.label_bounds.y+c.label_bounds.height/2});
            std::cout << ",\"paint_rects\":";paint_rects(c);
            std::cout << ",\"text\":";control_text(c,p==1);std::cout << '}';
        }
        std::cout << "],\"header_text\":[";
        const auto& service=l.controls[2].bounds;
        const auto& save=l.controls[3].bounds;
        const auto& flat=l.controls[9].bounds;
        const float left=service.x+service.width+12,right=save.x-12;
        // Centering gives the same title x. Height is chosen so top equals the
        // direct paint_header text top; shadow is separately documented.
        const float request=l.show_cabinet ? 40.0F : 28.0F;
        const float size=std::min(request,request*(right-left)/advance("TONEWHEEL ATLAS",request,font_data::kSerif));
        text_sample("title","TONEWHEEL ATLAS",{left,l.header.y+(l.show_cabinet ? 4.0F : 8.0F),right-left,size*1.2F},size,true,0);
        std::cout << ',';text_sample("caption","NOMINAL DRY ORGAN",{left,l.header.y+l.header.height-29,
            std::max(0.0F,flat.x-left-10),22},11);std::cout << "]}";
    }
    std::cout << "]}\n";
}
