#include "hammond/RotaryRenderer.h"
#include "tests/reference/rotary_waveform_reference.h"
#include "src/RotaryRendererInternal.h"
#include <array>
#include <chrono>
#include <iostream>
using namespace hammond::rotary;
namespace ref=rotary_waveform_reference;
int main(){
 auto scene=ref::full_scene(); Profile p;p.sound_speed_m_s=scene.sound_speed_m_s;p.reference_distance_m=scene.reference_distance_m;
 for(std::size_t i=0;i<2;++i){const auto& s=scene.rotors[i];p.rotors[i]={{s.origin_m.x,s.origin_m.y,s.origin_m.z},s.radius_m,{s.slow_rad_s,s.fast_rad_s,s.tau_up_s,s.tau_down_s,static_cast<std::int8_t>(s.direction)},s.initial_phase_rad,s.initial_speed_rad_s,SpeedCommand::Chorale};const auto m=scene.microphones[i];p.microphones[i]={{m.x,m.y,m.z}};}
 RotaryRenderer r;if(r.prepare(p,{48000,4096})!=Status::Ok)return 1;
 std::array<double,4096>a{},b{},l{},rr{}; a[0]=1;
 const auto start=std::chrono::steady_clock::now();double residual=0;std::uint32_t evaluations=0;
 for(int block=0;block<24;++block){const auto x=r.process(a,b,l,rr);if(!x){std::cerr<<status_name(x.status)<<'\n';return 2;}residual=std::max(residual,x.max_solver_residual_s);evaluations=std::max(evaluations,x.max_solver_iterations);}
 const double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
 std::cout<<"frames="<<r.state().frame<<" seconds="<<elapsed<<" frames_per_second="<<static_cast<double>(r.state().frame)/elapsed<<" max_residual="<<residual<<" max_evaluations="<<evaluations<<" storage_bytes="<<sizeof(detail::RotaryRendererStorage)<<'\n';
}
