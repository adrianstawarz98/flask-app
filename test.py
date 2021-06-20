input_shape = (128,128, 3)

base_model = keras.applications.InceptionResNetV2(weights='imagenet', 
                                include_top=False, 
                                input_shape=(128,128,3))
base_model.trainable = False

model1 = base_model.output
model1 = GlobalAveragePooling2D()(model1)
# let's add a fully-connected layer
model1 = Dense(2048, activation='relu')(model1)
model1= BatchNormalization()(model1)
model1=Dropout(0.3)(model1)
model1= Dense(64,activation='relu')(model1)
model1= BatchNormalization()(model1)
model1=Dropout(0.3)(model1)
# and a logistic layer -- let's say we have 200 classes
predictions = Dense(2, activation='softmax')(model1)
for layer in base_model.layers:
    layer.trainable = False

# this is the model we will train
model=Sequential()
model = Model(inputs=base_model.input, outputs=predictions)
model.compile(loss='sparse_categorical_crossentropy', 
              optimizer='RMSprop',
              metrics=['accuracy'])
