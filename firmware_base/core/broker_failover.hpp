// ARMOR-NODE-HMI - the rule of the broker watchdog when the connection is DOWN: when to start a client that could not be made and when to move to the next saved broker. No hardware.
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.
//
// Every round (about ten seconds apart) the node's watchdog tells this class whether a client exists and how many brokers are saved. A client that does not exist is made again after a
// few rounds; a client that stays down moves the node to the next saved broker (wrapping to the first) after the same number of rounds, and only when there is another one to move to.
// A connected round forgets the count. The way BACK to the first broker while connected is linkwatch::BackupReturn's. The node's task only carries out the answer.
#pragma once

namespace armor::brokerfail {

constexpr int kBadRoundsBeforeAct = 3;   // about thirty seconds of silence at one round every ten

enum class Action {
  kNone,          // nothing to do this round
  kRestartSame,   // there is no client (it could not be created or started): build it again for the broker in use
  kSwitchNext,    // the client stays down and another broker is saved: use `next_index`
};

struct Step {
  Action action = Action::kNone;
  int next_index = 0;   // the broker to use after the action
};

class Failover {
 public:
  explicit Failover(int bad_rounds_before_act = kBadRoundsBeforeAct) : limit_(bad_rounds_before_act < 1 ? 1 : bad_rounds_before_act) {}

  // One round with the connection down. `broker_index` is the broker in use (0 the first), `broker_count` how many are saved (1 + backups).
  Step down_round(bool has_client, int broker_index, int broker_count) {
    Step step;
    step.next_index = broker_index;
    if (!has_client) {
      if (++bad_ >= limit_) { bad_ = 0; step.action = Action::kRestartSame; }
      return step;
    }
    if (broker_count <= 1) return step;   // nowhere else to go
    if (++bad_ < limit_) return step;
    bad_ = 0;
    step.action = Action::kSwitchNext;
    step.next_index = (broker_index + 1) % broker_count;
    return step;
  }
  // The connection works (or was just replaced): the count starts again.
  void connected_round() { bad_ = 0; }
  int bad_rounds() const { return bad_; }

 private:
  int limit_;
  int bad_ = 0;
};

}  // namespace armor::brokerfail
