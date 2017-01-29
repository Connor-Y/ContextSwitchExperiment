#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <assert.h>
#include <time.h>
#include <inttypes.h>
#include <sched.h>
#include "tsc.h"

/*
What we want:
Find the clockspeed of the CPU

Basic Idea:
Count the number of cycles that occur over X seconds, then divide by X.
*/

// convert to ms?
float find_clock_speed(long num_nanseconds) {
	long nano_to_sec = 1000000000L;
	int num_sec = 0;
	long remaining_nanoseconds = num_nanseconds;
	if (num_nanseconds >= nano_to_sec) {
		num_sec = (int)num_nanseconds/nano_to_sec;
		remaining_nanoseconds = num_nanseconds % nano_to_sec;
	}
	struct timespec sleep;
	sleep.tv_sec = num_sec;
	sleep.tv_nsec = remaining_nanoseconds;
	
	u_int64_t old_counter = get_counter();
	nanosleep(&sleep, NULL);
	u_int64_t new_counter = get_counter();
	
	//printf("Counter Diff: %lu, divisor: %f\n",new_counter - old_counter, (((float)num_nanseconds)/nano_to_sec));
	return (new_counter - old_counter)/(((float)num_nanseconds)/nano_to_sec);
}

void get_clock_data(float *samples, int sample_size, int sleep_time) {
	// Get a number of sample clock speeds.
	int i = 0;
	//printf("Get clock data\n");
	while (i < sample_size) {
		samples[i] = find_clock_speed(sleep_time); 
		i++;
	}
}

int compare(const void *a,const void *b) {
	double *x = (double *) a;
	double *y = (double *) b;
	// return *x - *y; // this is WRONG...
	if (*x < *y) 
		return -1;
	else 
		if (*x > *y) 
			return 1; 
	
	return 0;
}

u_int64_t k_best_helper(float *clock_speed_samples, int size, int k_to_find, int tolerance) {
	int j = 0;
	int k = 0;
	int index_start = -1;
	while (j < size-1) {
		if (k >= k_to_find) {
			break;
		}
		if (clock_speed_samples[j+1] - clock_speed_samples[j] <= tolerance) {
			if (index_start == -1) {
				index_start = j;
			}
			k++;
		} else {
			k = 0;
			index_start = -1;
		}
		j++;
	}
	
	if (k == 0) {
		return -1;
	} else {
		u_int64_t ret = 0;
		int l = 0;
		while (l < k) {
			ret = ret + (u_int64_t)clock_speed_samples[index_start + l];
			l++;
		}
		return ret/k;
	}
	
}

// Look for clusters of data
u_int64_t k_best(int tolerance, int k_to_find, int sample_size, int sleep_time, int max_size) {
	if (sample_size > max_size) {
		sample_size = max_size;
	}
	float clock_speed_data[max_size];
	u_int64_t k_best_value = -1;
	int size = 0;
	while (k_best_value == -1 && size <= max_size) {
		get_clock_data(clock_speed_data, sample_size, sleep_time);
		size = size + sample_size;
		qsort(clock_speed_data, size, sizeof(float), compare); 
		k_best_value = k_best_helper(clock_speed_data, sample_size, k_to_find, tolerance);
	} 
	
	// If we still couldn't find a bunch, try again with new data.
	/*
	if (k_best_value == -1 && max_size > sample_size) {
		return k_best(tolerance, k_to_find, sample_size, sleep_time, max_size-sample_size);
	} */
	
	return k_best_value;

	

}



float convert_to_ms(u_int64_t num_cycles, float clock_speed) {
	return num_cycles/clock_speed;
}


/*
What we want: 
A trace of active and inactive periods.

Basic Idea:
Have the program countinally call a function which checks the cycle counter value.
If the value is less than the threshold, the program was running constantly*.
If the value is greater than threshold, it paused to do something else before comming
back to the process.
*/
// Do we want the loop inside or outside this func?
int inactive_periods(int num, u_int64_t threshold, u_int64_t *samples, int set_zero_flag) {
	int sample_index = 0;
	u_int64_t counter = 0;
	u_int64_t old_counter = 0;
	int i = 0;
  if (!set_zero_flag) {
    start_counter();
  }
	while (i < num) {
		counter = get_counter();
		if (counter - old_counter > threshold) {
			// We were inactive
			samples[sample_index] = old_counter;
			samples[sample_index+1] = counter;
			sample_index = sample_index + 2;
			i++;
		} 		
		// Update Counter
		old_counter = counter;

	}
	// Return the index of the last element (off by 1?)
	return sample_index;
}



/*
What we want:
Print samples array to produce a trace.

Basic Idea:
samples array contains start and stop for each inactive period. 
Thus we simply need to take the differences to find the active and inactive times.
*/
void make_trace(int num_nanosecs, int sample_size, int threshold, int set_zero_flag) {
	// Start the counter
  if (!set_zero_flag) {
    start_counter();
  }
	// TODO: reset clockspeed to kbest method
	// Get clock speed using k-best method
	u_int64_t clock_speed = 0;
	while (clock_speed <= 0) {
		clock_speed = k_best(50000, 3, 10, num_nanosecs, 20)/1000;
	}
	//printf("Clock speed %lu\n", clock_speed);
	int count = 0;
	
	// 2*sample_size because we need to store a start and stop for each sample.
	u_int64_t samples[2*sample_size];
	// Reset the counter

	int size = inactive_periods(sample_size, threshold, samples, set_zero_flag);
	
	printf("Active 0: start at 0, duration %lu cycles (%f ms)\n", 
				samples[count], samples[count]/(float)clock_speed);
	
	while (count < size-1) {
		u_int64_t num_cycles = samples[count+1] - samples[count];
		if (count % 2 == 0) {
			// Inactive
			printf("Inactive %d: start at %lu, duration %lu cycles (%f ms)\n", 
				(count+1)/2, samples[count], num_cycles, num_cycles/(float)clock_speed);

		} else {
			// Active
			printf("Active %d: start at %lu, duration %lu cycles (%f ms)\n", 
				(count+1)/2,  samples[count], num_cycles, num_cycles/(float)clock_speed);
		}
		count++;
	}	
	
  
}


int main(int argc, const char* argv[])
{
	// Limit code to 1 cpu
	cpu_set_t my_set;        
	CPU_ZERO(&my_set);      
	CPU_SET(0, &my_set);   
	sched_setaffinity(0, sizeof(cpu_set_t), &my_set);
	
  int set_zero_flag = 0;
  int interval = 20;
  if (argc == 3){
    set_zero_flag = 1;
  } 
  if (argc >= 2) {
    interval = atoi(argv[1]);
  }
  
	// Keep in mind that threshold is in cycles
	make_trace(500000000L, interval, 5000, set_zero_flag);
	
	return 0;
}


/*
What we want:
Need to produce output suitable for GNUPlot or other graphic software

Basic Idea:
Look into gnuplot.


What we want:
Look at driver.py and a1gnuploy.py


	
	



Report Questions:
Take a look at /proc/interupts for an idea of what interupts occur before and during (after execution finishes) the program

Questions:
1. With what frequency do timer interrupts occur?
This should be a regular occurence every X cycles.

2. How long does it take to handle a timer interrupt?
This should take roughly the same amount of time with no other load
But will take longer if the interupt leads to other tasks being processed

3. If it appears that there are other, non-timer interrupts (that is, other short periods of inactivity that don't fit the pattern of the periodic timer interrupt), explain what these are likely to be, based on what you can determine about other activity on the system you are measuring.
If they are short, it may be the pc handling user input like the mouse/keyboard input or other high priority tasks

4. Over the period of time that the process is running (that is, without lengthy interruptions corresponding to a switch to another process), what percentage of time is lost to servicing interrupts (of any kind)?


----
Context Switches:
What we want:
Measure how long the context switch time is.

Basic Idea:
Run two programs that each keep track of when they are active and inactive.
Use a third program to compare the data against each other.
We are looking for the gap in time when one program stops and the other starts.
Make sure to minimize other processes when running this.

T: Could run more than 2 programs but that makes combining data more work




What I need to do is create a modified trace maker to run and output to a file.
We run this twice, generating two files which we can then read into the combiner.
I probably want to rewrite the combiner in python so that I can use re.match() to handle the original maketrace.

*/

/*
// Active 0-1, inactive 1-2, active 2-3 ...
void data_combiner(int tolerance, u_int64_t *data1, u_int64_t *data2, int size1, int size2, u_int64_t *results) {
	int c1 = 0;
	int c2 = 0;
	int count = 0;
	while (c1 < size1 -1 && c2 < size2 - 1) {
		u_int64_t start1 = data1[c1];
		u_int64_t stop1 = data1[c1+1];
		u_int64_t start2 = data2[c2];
		u_int64_t stop2 = data1[c2+1];
		
		// Note: Need to make sure that only one proc is running at a time
		// i.e. one cpu only
		if (stop1 < start2 && stop1 + tolerance >= start2) {
			results[count] = start2-stop1;
			// We only want the active portion of each code
			c1 = c1 + 2;
			count = count + 1;	
		} else (stop2 < start1 && stop2 + tolerance >= start1){
			results[count] = start1-stop2;
			// We only want the active portion of each code
			c2 = c2 + 2;
			count = count + 1;	
		}
		
	}
	
	return count; 
}

void printer(u_int64_t *data, int size) {
	int i = 0;
	while (i < size) {
		printf("id=%d value=%lu", i, data[i]);
	}

}
*/

