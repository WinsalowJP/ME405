# Team 14 RedbullRomi, ME 405 Time Trial Competition

The goal of the project was to participate in a Romi Robot time trial competition. All participants were required to use a Romi Robot equipped with an STM32L476 Nucleo board, which was mounted on a custom PCB (ShoeOfBrian03C.brd) programmed to run MicroPython. It was up to the competitors to supply the rest of the hardware needed.

Overall, we were able to get the ROMI up and running. Our ROMI was able  to complete the circuit in about 21 seconds after a 5 second deduction for moving a cup. 

## RedBull Romi 
![RedbullRomi](https://winsalowjp.github.io/ME405/images/redbullromi.png "RedbullRomi")


Here is a link to the video of our demo in class ----> [Click Here for YouTube video](https://youtu.be/oJEXl1eLnzM?si=zaIdsHXoJzN_Ktf9).


## Hardware Layout
We started out with the base Romi robot chassis, a nucleo board, and a ShoeOfBrian03C board.

![Romi Chassis](https://winsalowjp.github.io/ME405/images/RomiBaseChassis.png "Romi Chassis")

Our ROMI was setup with a minimal amount of sensors. As you can see in the image below, the wiring diagram is relatively simple as we did not add
a bluetooth module or a bump sensor. 

![Hardware Wiring Diagram](https://winsalowjp.github.io/ME405/images/wiring.png "This is a hardware wiring diagram.")

We went with a simpler approach by using the accelerometer on the IMU to detect bumps and developed our ROMI using simple code that was easy to tweak and test without utilizing a bluetooth module like many other groups. 

<div style="display: flex; gap: 20px;">
  <div>
    <table border="1" cellspacing="0" cellpadding="4">
      <thead>
        <tr>
          <th colspan="2">Right Motor | Nucleo L476RG</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>SLP</td>
          <td>PC9</td>
        </tr>
        <tr>
          <td>DIR</td>
          <td>PB12</td>
        </tr>
        <tr>
          <td>PWM</td>
          <td>PA5</td>
        </tr>
        <tr>
          <td> Encoder CH1</td>
          <td>PB6</td>
        </tr>
        <tr>
          <td> Encoder CH2</td>
          <td>PB7</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div>
    <table border="1" cellspacing="0" cellpadding="4">
      <thead>
        <tr>
          <th colspan="2">Left Motor | Nucleo L476RG</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>SLP</td>
          <td>PA10</td>
        </tr>
        <tr>
          <td>DIR</td>
          <td>PA7</td>
        </tr>
        <tr>
          <td>PWM</td>
          <td>PA0</td>
        </tr>
        <tr>
          <td> Encoder CH1</td>
          <td>PC6</td>
        </tr>
        <tr>
          <td> Encoder CH2</td>
          <td>PC7</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<div style="display: flex; gap: 20px;">
  <!-- IMU (BNO055) Table -->
  <div>
    <table border="1" cellspacing="0" cellpadding="4">
      <thead>
        <tr>
          <th colspan="2">IMU (BNO055) | Nucleo L476RG</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>SDA</td>
          <td>PB10</td>
        </tr>
        <tr>
          <td>SCL</td>
          <td>PB11</td>
        </tr>
        <tr>
          <td>VCC</td>
          <td>5V</td>
        </tr>
        <tr>
          <td>GND</td>
          <td>GND</td>
        </tr>
      </tbody>
    </table>
  </div>
  
  <!-- LineSensor Table -->
  <div>
    <table border="1" cellspacing="0" cellpadding="4">
      <thead>
        <tr>
          <th colspan="2">LineSensor | Nucleo L476RG</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Sensor1 (L)</td>
          <td>PA1</td>
        </tr>
        <tr>
          <td>Sensor2</td>
          <td>PA4</td>
        </tr>
        <tr>
          <td>Sensor3</td>
          <td>PB0</td>
        </tr>
        <tr>
          <td>Sensor4</td>
          <td>PC0</td>
        </tr>
        <tr>
          <td>Sensor5</td>
          <td>PC1</td>
        </tr>
        <tr>
          <td>Sensor6</td>
          <td>PC2</td>
        </tr>
        <tr>
          <td>Sensor7</td>
          <td>PC3</td>
        </tr>
        <tr>
          <td>Sensor8 (R)</td>
          <td>PC4</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

</table>

For a detailed reference on the pin locations of the Nucleo board, consult the image below, which is sourced from the official documentation provided by the board's manufacturer.

![NUCLEO-L476RG](https://winsalowjp.github.io/ME405/images/nucleo_wiring.png "NUCLEO-L476RG")

For a more comprehensive understanding of the board's specifications, please consult the official NUCLEO-L476RG documentation provided in the PDF link below.

[NUCLEO-L476RG Documentation](https://winsalowjp.github.io/ME405/images/stm32l476rg.pdf)


## Tasks

Our ROMI essentially ran on one task with everything built in. In hindsight, it probably was not the best idea to implement it like that, but it reduced the complexity of our system and helped narrow a lot of issues or prevented a lot of issues from coming up due to its simplicity.  Below is a simple task diagram showing how everything functions.

![Task diagram](https://winsalowjp.github.io/ME405/images/task_diagram.png "This is the task diagram.")

Here is a brief summary of each task:
* `button_task` was given the highest priority in our scheduler due to debugging purposes. It served as an emergency stop to disable the motors in development
* `user_task` is our terminal input for when the ROMI was wired up to our computers for debugging and testing.
* `encoder_update` updated the encoder at a regular interval every 10ms.
* `t4` was the name we gave our running task. It held the lowest priority due to the nature of the other tasks. 

# Running ROMI from One Task (t4)

Here is an FSM diagram detailing the states that drove the actions of ROMI, although lacking in specific details, you will have to check the actual code for more details.

![FSM diagram](https://winsalowjp.github.io/ME405/images/fsm1.png "This is a simple FSM diagram")

The ROMI was primarily hard-coded when it came to encoder position and absolute angle. We used the Euler angles from the BNO055 IMU to keep track of the ROMI's angle starting from the beginning of the program, up until it finishes the track.


# Documentation
Here is the link to our full documentation of the code throguh an HTML site made with Doxygen

[Click Here for Documentation!!](https://winsalowjp.github.io/ME405/docs/index.html)

