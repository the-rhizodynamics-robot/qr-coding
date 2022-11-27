I was having trouble using MS Word to create printable QR labels so I wrote this script to do it for me.  I use these to label growth containers for doing automated, high-throughput time lapse imaging of growing plants. In a separate script I decode the identity of the individual growth containers via the QR code. 

The script will take contents of labels.csv and create a printable sheet of labels. The program reads in the csv and encodes
the contents of the "label" column in a QR code on the left, and the concatenation of the label text and "description" on the 
right (in human readable form). There isn't much space for text so brevity is useful. Also (somewhat obviously) the labels and 
descriptions are stored in a csv file, which means they cannot contain commas.

I use the following labels: OL1735WR from onlinelabels.com. These are 48 labels/sheed (4 x 12). The dimensions of the sheet have
been emprirically determined and are hardcoded in this script. It shouldn't be difficult to reconfigure the script to create QR 
codes in an arbitrary arrangement.