#pragma once
#include <array>
#include <cmath>
#include <stdexcept>
#include <string_view>
#include <cstdint>
namespace p3n {
struct Profile { std::string_view id, name; };
inline constexpr std::array<Profile,8> profiles{{
 {"x","Pokemon X"},{"y","Pokemon Y"},{"omega-ruby","Pokemon Omega Ruby"},
 {"alpha-sapphire","Pokemon Alpha Sapphire"},{"sun","Pokemon Sun"},{"moon","Pokemon Moon"},
 {"ultra-sun","Pokemon Ultra Sun"},{"ultra-moon","Pokemon Ultra Moon"}}};
struct Settings { int render_fps=30; int speed=1;
 void validate() const { if ((render_fps!=30 && render_fps!=60) || (speed!=1 && speed!=2 && speed!=4 && speed!=8)) throw std::invalid_argument("unsupported timing setting"); }
};
// Presentation rate is independent of the synthetic 30 Hz guest clock.
// This is NOT a retail-game timing patch.
class Clock {
 double accumulator_=0;
 public:
 std::uint64_t advance(double seconds,int speed) {
  Settings{30,speed}.validate();
  if (!std::isfinite(seconds) || seconds<0) throw std::invalid_argument("invalid elapsed time");
  accumulator_ += seconds*30*speed;
  auto ticks=static_cast<std::uint64_t>(std::floor(accumulator_+1e-9));
  accumulator_-=static_cast<double>(ticks); return ticks;
 }
};
class Runtime {
 public: virtual ~Runtime()=default;
 virtual bool is_game() const=0;
 virtual void step(std::uint64_t)=0;
 virtual std::uint64_t ticks() const=0;
};
class MockRuntime final: public Runtime {
 std::uint64_t ticks_=0;
 public: bool is_game() const override {return false;}
 void step(std::uint64_t n) override {ticks_+=n;}
 std::uint64_t ticks() const override {return ticks_;}
};
}
