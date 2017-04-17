from input.read_input import read_google
import numpy as np
import time
from pprint import *
import copy
import cProfile
import math
import random


class Solution:
    first_call = True
    data = None
    default_latencies = []
    capacity = None

    def __init__(self, data=None, condition=None):

        if self.first_call:
            # print("first")
            self.first_call = False
            self.data = data
            self.set_default_latencies()
            self.capacity = self.data["cache_size"]
        self.cache_spaces = {}
        self.cache_contents = {}
        self.min_latencies = {}
        if condition == "empty":
            self.generate_empty()
        elif condition == "random":
            self.generate_random()


    def generate_empty(self):

        # initialise an empty set for each cache
        # set each cache space to 0, as it doesn't contain any video
        # for cache in range(self.data["number_of_caches"]):
        #     self.cache_contents[cache] = set()
        #     self.cache_spaces[cache] = 0
        self.add_caches()

        # set minimum latencies for each endpoint and video as the latency from the datacentre
        # for video in range(self.data["number_of_videos"]):
        #     self.min_latencies[video] = self.default_latencies[:]
        # self.add_latencies()

    def add_caches(self):
        for cache in range(self.data["number_of_caches"]):
            self.cache_contents[cache] = set()
            self.cache_spaces[cache] = 0

    def add_latencies(self):
        for video in range(self.data["number_of_videos"]):
            self.min_latencies[video] = self.default_latencies[:]
        # self.min_latencies = copy.deepcopy(self.default_latencies)

    def generate_random(self):

        # for video in range(self.data["number_of_videos"]):
        #     self.min_latencies[video] = self.default_latencies[:]
        # self.add_latencies()

        for cache in range(self.data["number_of_caches"]):
            self.cache_contents[cache] = set()
            self.cache_spaces[cache] = 0
            can_add = True

            while can_add:
                rand_vid = random.randint(0, self.data["number_of_videos"] - 1)
                if self.cache_spaces[cache] + self.data["video_size_desc"][rand_vid] <= self.capacity:
                    if rand_vid in self.data["video_ed_request"]:
                        self.cache_contents[cache].add(rand_vid)
                        self.cache_spaces[cache] += self.data["video_size_desc"][rand_vid]
                        self.update_min_latency(rand_vid, cache)

                else:
                    can_add = False


    def update_min_latency(self, video, cache):
        self.insert_latencies(video)

        for endpoint in self.data["video_ed_request"][video]:

            # list of caches connected to an endpoint
            connections = self.data["ed_cache_list"][endpoint]

            if cache in connections:
                current_smallest = self.min_latencies[video][endpoint]
                cache_lat = self.data["ep_to_cache_latency"][endpoint][cache]
                if cache_lat < current_smallest:
                    self.min_latencies[video][endpoint] = cache_lat

    def set_default_latencies(self):
        # set minimum latencies for each endpoint and video as the latency from the datacentre
        # for video in range(self.data["number_of_videos"]):
        #     self.default_latencies[video] = []
        for i in range(self.data["number_of_endpoints"]):
            self.default_latencies.append(self.data["ep_to_dc_latency"][i])

    def insert_latencies(self, video):
        if video not in self.min_latencies:
            self.min_latencies[video] = self.default_latencies[:]


    def valid_move(self, cache, video):
        # check if video is already in cache
        if video in self.cache_contents[cache]:
            return False

        # check whether adding the video will exceed cache size
        return self.cache_spaces[cache] + self.data["video_size_desc"][video] <= self.data["cache_size"]


    def score_change(self, video, cache):

        self.insert_latencies(video)
        if video not in self.data["video_ed_request"]:
            return 0

        # time taken to stream all videos from datacentre
        time_saved = 0

        for endpoint in self.data["video_ed_request"][video]:

            num_of_requests = self.data["video_ed_request"][video][endpoint][0]

            # list of caches connected to an endpoint
            connections = self.data["ed_cache_list"][endpoint]

            if cache in connections:
                current_smallest = self.min_latencies[video][endpoint]
                cache_lat = self.data["ep_to_cache_latency"][endpoint][cache]
                if cache_lat < current_smallest:
                    time_saved += (current_smallest - cache_lat) * num_of_requests

        return time_saved


    def score(self):

        # time taken to stream all videos from datacentre
        time_saved = 0
        total_requests = 0

        # form of request is as follows: (video, endpoint): num_of_requests, min_latency? can't remember to be honest
        for video in self.data["video_ed_request"]:
            for endpoint in self.data["video_ed_request"][video]:

                num_of_requests = self.data["video_ed_request"][video][endpoint][0]
                dc_latency = self.data["ep_to_dc_latency"][endpoint]

                # list of caches connected to an endpoint
                connections = self.data["ed_cache_list"][endpoint]
                # list of latencies of caches with video
                caches = [dc_latency, ]

                # find lowest latency cache with video.
                # if ep and cache have no connection, nothing happens
                for cache in connections:
                    if video in self.cache_contents[cache]:
                        caches.append(self.data["ep_to_cache_latency"][endpoint][cache])

                # check whether the smallest latency among the connected caches is smaller than the currently stored smallest latency
                # if it is, the currently stored smallest latency is updated
                self.insert_latencies(video)
                smallest_lat = self.min_latencies[video][endpoint]
                min_cache = min(caches)
                if min_cache < smallest_lat:
                    self.min_latencies[video][endpoint] = min_cache

                time_saved += ((dc_latency - min_cache) * num_of_requests)
                total_requests += num_of_requests

        return (time_saved * 1000) // total_requests




    def hill_climb(self):

        move_found = True
        while move_found:
            best_score = 0
            best_move = []
            move_found = False

            for cache in range(self.data["number_of_caches"]):
                for video in range(self.data["number_of_videos"]):
                    if self.valid_move(cache, video):

                        # have to order these backwards because of how the scoring function works
                        newscore = self.score_change(video, cache)
                        if newscore > best_score:
                            best_score = newscore
                            best_move = [cache, video]
                            move_found = True
                        elif newscore == best_score and newscore > 0:
                            rand = random.randint(0, 1)
                            if rand:
                                best_score = newscore
                                best_move = [cache, video]
                                move_found = True

            if move_found:
                # print("Best move is", best_move, "with score:", best_score)
                cache, video = best_move[0], best_move[1]
                self.cache_contents[cache].add(video)
                self.cache_spaces[cache] += self.data["video_size_desc"][video]

                # need to do this to reset the minimum latency for each request.
                # test which one is faster
                # results: It doesn't make much of a difference. update_min_latency is about 5-10% faster.
                self.insert_latencies(video)
                self.update_min_latency(video, cache)
                # print(score(solution, data))


class Population:

    def __init__(self, data):
        self.data = data
        self.POP_SIZE = 50
        self.MUTATION_RATE = 100
        self.members = []
        self.member_scores = [0 for x in range(self.POP_SIZE)]
        self.max_score = 0
        self.generation = 0
        self.generate_pop()

    def generate_pop(self):
        for i in range(1):
            newmember = Solution(self.data, "empty")
            newmember.hill_climb()
            # print(newmember)
            self.members.append(newmember)
            self.member_scores[i] = newmember.score()
            if self.member_scores[i] > self.max_score:
                self.max_score = self.member_scores[i]

        for i in range(1, self.POP_SIZE):
            newmember = Solution(self.data, "random")
            # print(newmember)
            self.members.append(newmember)
            self.member_scores[i] = newmember.score()
            if self.member_scores[i] > self.max_score:
                self.max_score = self.member_scores[i]

    def breed(self):
        new_pop = []
        new_member_scores = [0 for x in range(self.POP_SIZE)]
        new_max = 0
        for i in range(self.POP_SIZE):
            newmember = self.crossover()
            # hill_climb(newmember, self.data)
            new_pop.append(newmember)
            new_member_scores[i] = newmember.score()
            if new_member_scores[i] > new_max:
                new_max = new_member_scores[i]

        self.members += new_pop
        self.member_scores += new_member_scores
        print("generation_max:", new_max)
        if new_max > self.max_score:
            self.max_score = new_max
        self.generation += 1
        self.trim()


    def trim(self):
        sorted_pop = sorted(range(len(self.member_scores)), key=lambda i:self.member_scores[i])

        trim_indexes = sorted_pop[-self.POP_SIZE:]
        new_pop = []
        new_scores = []
        for i in trim_indexes:
            new_pop.append(self.members[i])
            new_scores.append(self.member_scores[i])
        self.members = new_pop
        self.member_scores = new_scores


    # inspired by https://www.youtube.com/watch?v=816ayuhDo0E&index=5#t=181.634703
    # gives a higher probability of being selected to members with a higher score
    def accept_reject(self):
        while True:
            partner = random.randint(0, self.POP_SIZE - 1)
            r = random.randint(0, self.max_score)

            if (r < self.member_scores[partner]):
                return partner


    def tournament_select(self, k):
        best_score = 0
        best_index = None

        second_score = 0
        second_index = None

        for i in range(k):
            index = random.randint(0, self.POP_SIZE - 1)
            cand_score = self.member_scores[index]
            if cand_score > best_score:
                second_score = best_score
                second_index = best_index
                best_score = cand_score
                best_index = index
            elif cand_score > second_score:
                second_score = cand_score
                second_index = index

        return best_index, second_index


    def crossover(self):
        # choose random partners, using accept reject
        # partner_a = self.members[self.accept_reject()]
        # partner_b = self.members[self.accept_reject()]

        # tournament select parents from 5% of the population
        partner_a, partner_b = self.tournament_select(self.POP_SIZE//20)
        partner_a = self.members[partner_a]
        partner_b = self.members[partner_b]

        child = Solution(self.data, "empty")

        for cache in range(len(child.cache_contents)):
            # # add all elements in partner_a and partner_b to a single set
            parent_dna = partner_a.cache_contents[cache].union(partner_b.cache_contents[cache])
            length = (len(partner_a.cache_contents[cache]) + len(partner_b.cache_contents[cache])) / 2
            length = math.ceil(length)

            potential_dna = random.sample(parent_dna, length)
            for video in potential_dna:
                video = self.mutate(video)
                if child.valid_move(cache, video):
                    child.cache_contents[cache].add(video)
                    child.cache_spaces[cache] += self.data["video_size_desc"][video]
        return child


    def mutate(self, dna):
        if random.randint(0, self.MUTATION_RATE) < 1:
            return random.randint(0, self.data["number_of_videos"] - 1)
        else:
            return dna



def sol_test(input_data):
    # start = time.clock()

    data = read_google(input_data)
    sols = []

    for i in range(2000):
        sols.append(Solution(data, "empty"))

    # solution.hill_climb()
    # print(solution.score())

    # print("Time taken:", time.clock() - start)


def pop_test(input_data, gens):
    data = read_google(input_data)
    population = Population(data)

    for i in range(gens):
        population.breed()
        print("Generation:", population.generation)
        print("Mean score:", np.mean(population.member_scores))
        print("Max score:", population.max_score, "\n")


if __name__=="__main__":
    start = time.clock()


    # data = read_google("input/me_at_the_zoo.in")
    # cProfile.run('sol_test("input/me_at_the_zoo.in")')
    cProfile.run('pop_test("input/me_at_the_zoo.in", 100)')
    # # me_at_the_zoo = 516740

    # sol = Solution(data)

    # cProfile.run("sol.generate_empty()")
    #
    # population = Population(data)

    # print(population.members)
    # for i in range(100):
    #     population.breed()
    #     print("Generation:", population.generation)
    #     print("Mean score:", np.mean(population.member_scores))
    #     print("Max score:", population.max_score, "\n")

    # sol = Solution(data)
    # sol.generate_empty()
    #
    # print(sol.cache_contents)
    # print(sol.score())
    # sol.hill_climb()
    # print(sol.score())
    #
    print("Time taken:", time.clock() - start)









