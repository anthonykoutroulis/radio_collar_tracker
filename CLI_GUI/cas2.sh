#!/bin/bash
# Constant configuration
GNU_RADIO_PIPELINE='/home/ntlhui/workspace/radio_collar_tracker/cw_detect/top_block.py'
# User supplied configuration
data_dir='/home/ntlhui/workspace/radio_collar_tracker_test/RUN_001075/'
run=1075

# Generated variables
num_raw_files=`ls ${data_dir} | grep 'RAW_DATA_' | wc -l`
num_collars=1
raw_file=`printf "%s/RUN_%06d.raw" ${data_dir} ${run}`
collar_file_prefix=`printf "%s/RUN_%06d_" ${data_dir} ${run}`

# Concatenate raw files together
for i in ${num_raw_files}
do
	cat `printf "%s/RAW_DATA_%06d_%06d" ${data_dir} ${run} ${i}` >> ${raw_file}
done
echo ${raw_file}

# Run through GNU Radio pipeline for each collar
for i in ${num_collars}
do
	# Get collar beat frequency
	frequency=-11583
	# Execute pipeline
	${GNU_RADIO_PIPELINE} -f ${frequency} -i ${raw_file} -o `printf "%s%06d.raw" ${collar_file_prefix} ${i}`
done

# For each collar, make map