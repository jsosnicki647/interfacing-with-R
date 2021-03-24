#sequence.index contains metadata on the 1,000 Human Genomes Project

import os
from IPython.display import Image
import rpy2.robjects as robjects
import rpy2.robjects.lib.ggplot2 as ggplot2
from rpy2.robjects.functions import SignatureTranslatedFunction
import pandas as pd
from rpy2.robjects import pandas2ri
from rpy2.robjects import default_converter
from rpy2.robjects.conversion import localconverter

#store r read.delim function into python variable
#read in sequence.index file
read_delim = robjects.r('read.delim')
seq_data = read_delim('sequence.index', header=True, stringsAsFactors=False)

#print column/row counts and column names
print('This data frame has %d columns and %d rows' % (seq_data.ncol, seq_data.nrow))
print(seq_data.colnames)

#store r functions as.integer and match in python variables
as_integer = robjects.r('as.integer')
match = robjects.r.match

#r match function returns the index of the location of the first vector within the second vector
selected_col = match('READ_COUNT', seq_data.colnames)[0] # Vector returned
print('Type of read count before as.integer: %s' % seq_data[selected_col - 1].rclass[0])

#r as.integer function converts type to integer
seq_data[selected_col - 1] = as_integer(seq_data[selected_col - 1])
print('Type of read count after as.integer: %s' % seq_data[selected_col - 1].rclass[0])

selected_col = match('BASE_COUNT', seq_data.colnames)[0] # Vector returned
seq_data[selected_col - 1] = as_integer(seq_data[selected_col - 1])

selected_col = match('CENTER_NAME', seq_data.colnames)[0]
seq_data[selected_col - 1] = robjects.r.toupper(seq_data[selected_col - 1])
robjects.r.assign('seq.data', seq_data)

robjects.r('seq.data <- seq.data[seq.data$WITHDRAWN==0, ]')
#Lets remove all withdrawn sequences

robjects.r("seq.data <- seq.data[, c('STUDY_ID', 'STUDY_NAME', 'CENTER_NAME', 'SAMPLE_ID', 'SAMPLE_NAME', 'POPULATION', 'INSTRUMENT_PLATFORM', 'LIBRARY_LAYOUT', 'PAIRED_FASTQ', 'READ_COUNT', 'BASE_COUNT', 'ANALYSIS_GROUP')]")
#Lets shorten the dataframe

#Population as factor
robjects.r('seq.data$POPULATION <- as.factor(seq.data$POPULATION)')

#SingnatureTranslatedFunction is a python representation of an R function
ggplot2.theme = SignatureTranslatedFunction(ggplot2.theme,
                                            init_prm_translate = {'axis_text_x': 'axis.text.x'})
bar = ggplot2.ggplot(seq_data) + ggplot2.geom_bar() + ggplot2.aes_string(x='CENTER_NAME') + ggplot2.theme(axis_text_x=ggplot2.element_text(angle=90, hjust=1))
robjects.r.png('bar.png', type='cairo-png')
bar.plot()

#close the plot
dev_off = robjects.r('dev.off')
dev_off()

#filter data on YRI and CEU populations
robjects.r('yri_ceu <- seq.data[seq.data$POPULATION %in% c("YRI", "CEU") & seq.data$BASE_COUNT < 2E9 & seq.data$READ_COUNT < 3E7, ]')
yri_ceu = robjects.r('yri_ceu')

#create scatter plot
scatter = ggplot2.ggplot(yri_ceu) + ggplot2.aes_string(x='BASE_COUNT', y='READ_COUNT', shape='factor(POPULATION)', col='factor(ANALYSIS_GROUP)') + ggplot2.geom_point()
robjects.r.png('scatter.png')
scatter.plot()
dev_off = robjects.r('dev.off')
dev_off()

