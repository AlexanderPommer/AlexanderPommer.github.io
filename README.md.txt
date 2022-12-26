Convolutional Neural Network Experimentation process

Convolutional layers `tf.keras.layers.Conv2D` of kernel sizes from 2 to 7 were tested, sizes 3 and 5 gave 
the best results.
1 to 3 hidden layers `tf.keras.layers.Dense` were tested, 3 gave the best results. A single layer resulted in
approximately 40% accuracy, 2 layers resulted in approximately 80% and 3 achieved >95% accuracy.
Dropout `tf.keras.layers.Dropout` values from 0.5 to 0 were tested, more central values performed better while
counteracting some overfitting.