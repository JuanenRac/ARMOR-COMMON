// ARMOR-NODE-HMI - host tests of the broker watchdog rule: a broker that stays down is left for the next saved one, a client that does not exist is built again, a working one is never touched.
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.
// A scripted broker stands in for the network: it answers or not at each round, and the test plays the node's task around the rule.
#include <cstdio>
#include <vector>

#include "../core/backoff.hpp"
#include "../core/broker_failover.hpp"

static int failures = 0;
#define CHECK(condition)                                                                        \
  do {                                                                                          \
    if (!(condition)) { ++failures; std::printf("FAIL %s:%d  %s\n", __FILE__, __LINE__, #condition); } \
  } while (0)

using namespace armor::brokerfail;

// The node's watchdog around the rule; only the broker `alive` answers (-1: none).
struct Node {
  Failover rule;
  int index = 0;
  int count;
  bool client = true;
  std::vector<int> switches;
  int restarts = 0;
  explicit Node(int brokers) : count(brokers) {}
  void round(int alive) {
    const bool connected = client && index == alive;
    if (connected) { rule.connected_round(); return; }
    const Step step = rule.down_round(client, index, count);
    if (step.action == Action::kSwitchNext) { index = step.next_index; switches.push_back(index); }
    if (step.action == Action::kRestartSame) { client = true; ++restarts; }
  }
};

static void test_it_waits_three_rounds_before_leaving() {
  Node node(3);
  node.round(2); node.round(2);
  CHECK(node.index == 0 && node.switches.empty());   // two silent rounds are not enough
  node.round(2);
  CHECK(node.index == 1);                            // the third moves to the next one
}

static void test_it_walks_the_list_and_stops_on_the_one_that_answers() {
  Node node(3);
  for (int i = 0; i < 30; ++i) node.round(2);
  CHECK(node.index == 2);
  CHECK(node.switches.size() == 2 && node.switches[0] == 1 && node.switches[1] == 2);
  for (int i = 0; i < 30; ++i) node.round(2);
  CHECK(node.index == 2 && node.switches.size() == 2);   // a broker that works is never left
}

static void test_it_wraps_to_the_first_when_none_answers_then_one_returns() {
  Node node(2);
  for (int i = 0; i < 6; ++i) node.round(-1);   // nobody answers: 0 -> 1 -> 0
  CHECK(node.index == 0 && node.switches.size() == 2 && node.switches[1] == 0);
  for (int i = 0; i < 6; ++i) node.round(1);
  CHECK(node.index == 1);
}

static void test_a_single_broker_is_never_left() {
  Node node(1);
  for (int i = 0; i < 50; ++i) node.round(-1);
  CHECK(node.index == 0 && node.switches.empty());
}

static void test_a_missing_client_is_built_again_after_three_rounds() {
  Node node(2);
  node.client = false;
  node.round(0); node.round(0);
  CHECK(!node.client && node.restarts == 0);
  node.round(0);
  CHECK(node.client && node.restarts == 1 && node.index == 0);   // same broker, no switch
}

static void test_a_connected_round_forgets_the_silence() {
  Node node(2);
  node.round(1); node.round(1);   // two silent rounds on broker 0
  node.round(0);                  // it answers
  node.round(1); node.round(1);   // two more silent ones: still not three in a row
  CHECK(node.index == 0 && node.switches.empty());
}

static void test_the_limit_is_never_below_one() {
  Failover rule(0);
  CHECK(rule.down_round(true, 0, 2).action == Action::kSwitchNext);
}

// The wait between tries of the client grows with the failures and falls back to the first wait when a try works (the Backoff the node uses for the broker).
static void test_the_retry_waits_grow_and_reset() {
  armor::retry::Backoff backoff(1000, 60000, 0);
  CHECK(backoff.next(0) == 1000 && backoff.next(0) == 2000 && backoff.next(0) == 4000);
  for (int i = 0; i < 20; ++i) backoff.next(0);
  CHECK(backoff.next(0) == 60000);
  backoff.reset();
  CHECK(backoff.next(0) == 1000);
}

int main() {
  test_it_waits_three_rounds_before_leaving();
  test_it_walks_the_list_and_stops_on_the_one_that_answers();
  test_it_wraps_to_the_first_when_none_answers_then_one_returns();
  test_a_single_broker_is_never_left();
  test_a_missing_client_is_built_again_after_three_rounds();
  test_a_connected_round_forgets_the_silence();
  test_the_limit_is_never_below_one();
  test_the_retry_waits_grow_and_reset();
  if (failures != 0) { std::printf("%d check(s) failed\n", failures); return 1; }
  std::printf("broker failover: all checks passed\n");
  return 0;
}
