#include "runtime.hpp"
#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>
#include <chrono>
#include <iostream>
#include <string>
int main(int argc,char** argv) {
 try {
 bool headless=false; int frames=0; p3n::Settings settings;
 for(int i=1;i<argc;++i) {
  std::string arg=argv[i];
  auto value=[&]() {if(i+1>=argc) throw std::invalid_argument("missing option value"); return std::string(argv[++i]);};
  if(arg=="--headless") headless=true;
  else if(arg=="--frames") {frames=std::stoi(value()); if(frames<=0) throw std::invalid_argument("frames must be positive");}
  else if(arg=="--fps") settings.render_fps=std::stoi(value());
  else if(arg=="--speed") settings.speed=std::stoi(value());
  else if(arg=="--run") {std::cerr<<"BLOCKED: no verified Pokemon game backend is integrated. Use tools/port.py for local conversion.\n";return 3;}
  else throw std::invalid_argument("unknown option: "+arg);
 }
 settings.validate(); p3n::MockRuntime runtime; p3n::Clock clock;
 if(headless) {if(!frames) frames=60;for(int i=0;i<frames;++i) runtime.step(clock.advance(1.0/settings.render_fps,settings.speed));
 std::cout<<"mode=MOCK game_executed=false frames="<<frames<<" guest_ticks="<<runtime.ticks()<<"\n";return 0;}
 if(!SDL_Init(SDL_INIT_VIDEO|SDL_INIT_GAMEPAD)) throw std::runtime_error(SDL_GetError());
 SDL_Window* window=nullptr; SDL_Renderer* renderer=nullptr;
 if(!SDL_CreateWindowAndRenderer("Pokemon 3DS Native - MOCK ONLY",960,720,0,&window,&renderer)) throw std::runtime_error(SDL_GetError());
 SDL_SetRenderLogicalPresentation(renderer,960,720,SDL_LOGICAL_PRESENTATION_LETTERBOX);
 int selected=1, rendered=0; bool running=true;
 auto last=std::chrono::steady_clock::now();
 std::cerr<<"mode=MOCK game_executed=false renderer="<<SDL_GetRendererName(renderer)<<"\n";
 while(running) {
 auto start=std::chrono::steady_clock::now(); SDL_Event e;
 while(SDL_PollEvent(&e)) {
  if(e.type==SDL_EVENT_QUIT) running=false;
  if(e.type==SDL_EVENT_KEY_DOWN) {
   switch(e.key.key) {
    case SDLK_ESCAPE: running=false;break;
    case SDLK_UP: selected=(selected+7)%8;break;
    case SDLK_DOWN: selected=(selected+1)%8;break;
    case SDLK_F: settings.render_fps=settings.render_fps==30?60:30;break;
    case SDLK_S: settings.speed=settings.speed==8?1:settings.speed*2;break;
    case SDLK_RETURN: SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_INFORMATION,"Game runtime unavailable","This is a MOCK launcher. No game code is running. Pokemon Y port verification is pending.",window);break;
   }
  }
  if(e.type==SDL_EVENT_GAMEPAD_BUTTON_DOWN) {
   if(e.gbutton.button==SDL_GAMEPAD_BUTTON_DPAD_DOWN) selected=(selected+1)%8;
   if(e.gbutton.button==SDL_GAMEPAD_BUTTON_DPAD_UP) selected=(selected+7)%8;
  }
 }
 runtime.step(clock.advance(std::chrono::duration<double>(start-last).count(),settings.speed));last=start;
 SDL_SetRenderDrawColor(renderer,15,20,32,255);SDL_RenderClear(renderer);
 SDL_SetRenderDrawColor(renderer,255,205,90,255);
 SDL_RenderDebugText(renderer,36,28,"MOCK ONLY - NO GAME EXECUTION / NO GAME ASSETS");
 SDL_SetRenderDrawColor(renderer,230,235,245,255);
 SDL_RenderDebugText(renderer,36,58,"UP/DOWN: profile   F: display FPS   S: synthetic speed   ENTER: status");
 for(int i=0;i<8;++i) {
  SDL_SetRenderDrawColor(renderer,i==selected?100:160,i==selected?230:170,220,255);
  SDL_RenderDebugTextFormat(renderer,36,110+i*30,"%s %s [UNVERIFIED]",i==selected?">":" ",p3n::profiles[i].name.data());
 }
 SDL_SetRenderDrawColor(renderer,70,100,150,255);
 SDL_FRect top{460,120,400,240},bottom{500,390,320,240};SDL_RenderFillRect(renderer,&top);SDL_RenderFillRect(renderer,&bottom);
 SDL_SetRenderDrawColor(renderer,255,255,255,255);
 SDL_RenderDebugText(renderer,475,140,"SYNTHETIC TOP SCREEN");SDL_RenderDebugText(renderer,515,410,"SYNTHETIC TOUCH SCREEN");
 SDL_RenderDebugTextFormat(renderer,36,660,"display=%d FPS synthetic speed=%dx ticks=%llu",settings.render_fps,settings.speed,static_cast<unsigned long long>(runtime.ticks()));
 SDL_RenderPresent(renderer);++rendered;if(frames && rendered>=frames) running=false;
 auto spent=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
 if(spent<1.0/settings.render_fps) SDL_Delay(static_cast<Uint32>((1.0/settings.render_fps-spent)*1000));
 }
 std::cerr<<"mode=MOCK frames="<<rendered<<" guest_ticks="<<runtime.ticks()<<"\n";
 SDL_DestroyRenderer(renderer);SDL_DestroyWindow(window);SDL_Quit();return 0;
 }catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<"\n";return 1;}
}
