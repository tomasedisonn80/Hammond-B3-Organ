#include "hammond/RotaryRenderer.h"
#include <array>
#include <cmath>
#include <iostream>
#include <vector>
using namespace hammond::rotary;
int main(){
 Profile p;
 p.sound_speed_m_s=300; p.reference_distance_m=1;
 p.microphones={MicrophoneProfile{{1,0,0}},MicrophoneProfile{{2,0,0}}};
 for(auto& r:p.rotors){r.motion={2,30,.3,.7,1};r.initial_speed_rad_s=2;}
 RotaryRenderer r; if(r.prepare(p,{48000,4096})!=Status::Ok)return 1;
 std::vector<double> a(4096),b(4096),l(4096),rr(4096);
 a[0]=1; a[20]=-.5; b[7]=.25;
 auto result=r.process(a,b,l,rr);
 std::cout<<status_name(result.status)<<" frame="<<r.state().frame<<" capacity="<<r.history_capacity_frames()<<" flush="<<r.tail_flush_frames()<<" left_impulse="<<l[162]<<" right_impulse="<<rr[322]<<" max_residual="<<result.max_solver_residual_s<<" evaluations="<<result.max_solver_iterations<<'\n';
 if(!result||r.state().frame!=4096||std::abs(l[162]-1)>1e-9||std::abs(rr[322]-.5)>1e-9)return 2;
 auto before=r.state();auto diagnostics=r.diagnostics();a[0]=2;std::fill(l.begin(),l.end(),7);
 result=r.process(a,b,l,rr);if(result.status!=Status::InvalidBuffer||r.state()!=before||r.diagnostics()!=diagnostics||l[0]!=7)return 3;
 const auto motion=r.state().motion; if(r.reconfigure_sample_rate(192000)!=Status::Ok||r.state().motion!=motion||r.state().frame!=0)return 4;
 if(r.reset()!=Status::Ok||r.state().sample_rate!=192000||r.state().motion[0].speed_rad_s!=2)return 5;
 return 0;
}
