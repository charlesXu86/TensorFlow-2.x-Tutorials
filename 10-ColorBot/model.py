import  tensorflow as tf
from    tensorflow import keras



class RNNColorbot(keras.Model):
    """
    Multi-layer (LSTM) RNN that regresses on real-valued vector labels.
    """

    def __init__(self, rnn_cell_sizes, label_dimension, keep_prob):
        """Constructs an RNNColorbot.
        Args:
          rnn_cell_sizes: list of integers denoting the size of each LSTM cell in
            the RNN; rnn_cell_sizes[i] is the size of the i-th layer cell
          label_dimension: the length of the labels on which to regress
          keep_prob: (1 - dropout probability); dropout is applied to the outputs of
            each LSTM layer
        """
        super(RNNColorbot, self).__init__(name="")

        self.rnn_cell_sizes = rnn_cell_sizes
        self.label_dimension = label_dimension
        self.keep_prob = keep_prob

        self.cells = [keras.layers.LSTMCell(size) for size in rnn_cell_sizes]
        self.relu = keras.layers.Dense(label_dimension, activation=tf.nn.relu)

    def call(self, inputs, training=None):
        """
        Implements the RNN logic and prediction generation.
        Args:
          inputs: A tuple (chars, sequence_length), where chars is a batch of
            one-hot encoded color names represented as a Tensor with dimensions
            [batch_size, time_steps, 256] and sequence_length holds the length
            of each character sequence (color name) as a Tensor with dimension
            [batch_size].
          training: whether the invocation is happening during training
        Returns:
          A tensor of dimension [batch_size, label_dimension] that is produced by
          passing chars through a multi-layer RNN and applying a ReLU to the final
          hidden state.
        """
        (chars, sequence_length) = inputs
        # Transpose the first and second dimensions so that chars is of shape
        # [time_steps, batch_size, dimension].
        chars = tf.transpose(chars, [1, 0, 2])
        # The outer loop cycles through the layers of the RNN; the inner loop
        # executes the time steps for a particular layer.
        batch_size = int(chars.shape[1])
        for l in range(len(self.cells)): # for each layer
            cell = self.cells[l]
            outputs = []
            # h_zero, c_zero
            state = (tf.zeros((batch_size, self.rnn_cell_sizes[l])),
                     tf.zeros((batch_size, self.rnn_cell_sizes[l])))
            # Unstack the inputs to obtain a list of batches, one for each time step.
            chars = tf.unstack(chars, axis=0)
            for ch in chars: # for each time stamp
                output, state = cell(ch, state)
                outputs.append(output)
            # The outputs of this layer are the inputs of the subsequent layer.
            # [t, b, h]
            chars = tf.stack(outputs, axis=0)
            if training:
                chars = tf.nn.dropout(chars, self.keep_prob)
        # Extract the correct output (i.e., hidden state) for each example. All the
        # character sequences in this batch were padded to the same fixed length so
        # that they could be easily fed through the above RNN loop. The
        # `sequence_length` vector tells us the true lengths of the character
        # sequences, letting us obtain for each sequence the hidden state that was
        # generated by its non-padding characters.
        batch_range = [i for i in range(batch_size)]
        # stack [64] with [64] => [64, 2]
        indices = tf.stack([sequence_length - 1, batch_range], axis=1)
        # [t, b, h]
        # print(chars.shape)
        hidden_states = tf.gather_nd(chars, indices)
        # print(hidden_states.shape)
        return self.relu(hidden_states)