#include "BFO.hpp"
#include <thread>
#include <mutex>
#include <cmath>
#include <complex>
#include "Sample.hpp"
#include <queue>

using namespace std;

BFO::BFO(int sample_rate, int frequency, CRFSample (*out_queue)()):sample_rate(sample_rate), OSC_freq(frequency), run_state(true){
	next_sample = out_queue;
	// Start worker thread associated with this class
	thread class_thread(&BFO::run, this);
}

BFO::~BFO(){
	run_state = false;
	class_thread.join();
}

CRFSample* BFO::getNextSample(){
	if(output_queue.empty()){
		return NULL;
	}
	output_queue_mutex.lock();
	CRFSample retval = output_queue.front();
	output_queue.pop();
	output_queue_mutex.unlock();
	return &retval;
}

void BFO::run(){
	while(run_state){
		// Get next sample
		CRFSample sample = next_sample();
		if(!sample){
			// TODO wait if necessary
			continue;
		}
		// Generate oscillator IQ
		double time = sample.getIndex() / sample.getSampleRate();
		complex bfo_sample = cos(frequency * time) + i * sin(frequency * time);
		// Multiply sample
		complex sig_sample = sample.get_data();
		sig_sample *= bfo_sample;
		sample.setData(sig_sample);
		// Queue sample
		output_queue_mutex.lock();
		while(signal_queue.size() >= QUEUE_SIZE_MAX){
			output_queue_mutex.unlock();
			// TODO force wait using posix wait
			output_queue_mutex.lock();
		}
		output_queue.push(sample);
		output_queue_mutex.unlock();
	}
}

