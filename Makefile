# Copyright 2015 Ubiquant Investment Co. 
# All rights reserved.

-include /inc/version.inc
-include /inc/ubiqtool.inc
-include /inc/eva.inc
-include /inc/redshift.inc

-include .para.inc

# Global Variables
CC=gcc
CPP=g++

# set CPPFLAGS
CPPFLAGS := -Wall -Wempty-body -Wno-deprecated -Wno-deprecated -std=c++11
CFLAGS :=

PREFIX=.
LIB_PATH=$(PREFIX)/lib
BIN_PATH=$(PREFIX)/bin
ETC_PATH=$(PREFIX)/etc
SRC_PATH=$(PREFIX)/src
DOC_PATH=$(PREFIX)/doc
BUILD_PATH=$(PREFIX)/build
INCLUDE_PATH=$(PREFIX)/include


INSTALL_PATH=/opt/version/${COMPILE_VERSION}

# 2 definitions used by ubiq version control system
DEV_VERSION=$(shell ./version.sh -s)
COMPILER_VERSION = $(shell $(CPP) -dumpversion)
UPDATE_BUILD := $(shell ./version.sh -m)
BUILD_VERSION := $(shell ./version.sh -b)


OPT_FLAGS := -O3 -DRELEASE -DNDEBUG -fomit-frame-pointer -fstrict-aliasing 
DEBUG_FLAGS :=  -g -O0 -DDEBUG 
BENCHMARK_FLAGS := -DBENCHMARK
DYNAMIC_FLAGS := -fPIC -shared
OBJ_FLAGS := -c

GIT_HEAD := $(shell grep GITHEAD .para.inc | cut -d'=' -f2)
UBIQ_DEF= -DGITHEAD='"$(GITHEAD)"' -DUBIQ_DEV_VERSION='"$(DEV_VERSION)"' -DUBIQ_DEV_COMPILER='"$(CPP)"' -DUBIQ_DEV_BUILD='"$(BUILD_VERSION)"' -DUBIQ_DEV_COMPILER_VERSION='"$(COMPILER_VERSION)"'

CPPFLAGS += $(UBIQ_DEF)
CFLAGS += $(UBIQ_DEF)

UBIQ_INC = -I${INSTALL_PATH}/include
UBIQ_LIB = -L${INSTALL_PATH}/lib -lubiqtool -lubiqlog -lrt -lpthread


#************************* INSTALL *********************
.PHONY: command util doc clean distclean install tags command


GRPC_INC=-I/opt/3rd/protobuf3/include -I/opt/3rd/grpc/include
GRPC_LIB=-L/opt/3rd/grpc/lib -lgrpc -lgrpc++
PROT_LIB=-L/opt/3rd/protobuf3/lib -lprotobuf

all: dealer

dealer:
	mkdir -p build
	mkdir -p cpp
	/opt/3rd/protobuf3/bin/protoc -Icommunicate --grpc_out=cpp/ --cpp_out=cpp/ --plugin=protoc-gen-grpc="/opt/3rd/grpc/bin/grpc_cpp_plugin" communicate/dealer.proto
	/opt/anaconda3/bin/python -m grpc_tools.protoc -Icommunicate/ --python_out=communicate/ --grpc_python_out=communicate/ communicate/dealer.proto
	sed -i 's/import dealer_pb2/from . import dealer_pb2/' communicate/dealer_pb2_grpc.py

#************************* CLEAN ************************
clean:: 
	@rm -rf $(TEST_OBJECTS) $(TARGET_OBJECTS)
	@rm -rf $(LIB_PATH)/*
	@rm -rf $(BIN_PATH)/* 	
	@rm -rf $(BUILD_PATH)/*
	@rm -rf runTests
	@rm -rf gmon.out
	@rm -rf ${program}

distclean: clean
	@rm -rf gmon.out
	@rm -rf core.*
	@rm -rf *~
	@rm -rf $(DOC_PATH)/*
	@rm -rf CMakeCache.txt CMakeFiles cmake_install.cmake 
rebuild:: clean all
