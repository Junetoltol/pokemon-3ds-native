#include "runtime.hpp"
#include <iostream>
int main(){
 for(int fps:{30,60}) for(int speed:{1,2,4,8}) {
 p3n::Clock clock; p3n::MockRuntime r;
 for(int i=0;i<fps*10;++i)r.step(clock.advance(1.0/fps,speed));
 if(r.is_game() || r.ticks()!=static_cast<unsigned>(300*speed)) return 1;
 }
 try {p3n::Settings{60,3}.validate();return 2;}catch(const std::invalid_argument&){}
 try {p3n::Clock c;c.advance(-1,1);return 3;}catch(const std::invalid_argument&){}
 std::cout<<"8 synthetic timing combinations passed; no retail-game validation\n";
}
