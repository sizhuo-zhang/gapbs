# See LICENSE.txt for license details.

CXX_FLAGS += -std=c++11 -O3 -Wall -I$(RISCY_HOME)/riscv_custom
PAR_FLAG = -fopenmp
BUILD_DIR = build/x86

ifneq (,$(findstring icpc,$(CXX)))
	PAR_FLAG = -openmp
endif

ifneq (,$(findstring sunCC,$(CXX)))
	CXX_FLAGS = -std=c++11 -xO3 -m64 -xtarget=native
	PAR_FLAG = -xopenmp
endif

ifneq ($(SERIAL), 1)
	CXX_FLAGS += $(PAR_FLAG)
endif

ifdef RISCV
	CXX = riscv64-unknown-linux-gnu-g++
	CXX_FLAGS += -static
	BUILD_DIR = build/riscv
endif

KERNELS = bc bfs cc cc_sv pr sssp tc
SUITE = $(addprefix $(BUILD_DIR)/,$(KERNELS) converter)

.PHONY: all
all: $(SUITE)

$(SUITE): $(BUILD_DIR)/% : src/%.cc src/*.h | $(BUILD_DIR)
	$(CXX) $(CXX_FLAGS) $< -o $@

$(BUILD_DIR):
	mkdir -p $@

# Testing
include test/test.mk

# Benchmark Automation
include benchmark/bench.mk


.PHONY: clean
clean:
	rm -f $(SUITE) test/out/*
