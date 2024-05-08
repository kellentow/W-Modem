# WModem Data Transfer Protocol Documentation

## 1. Overview

- The WModem Data Transfer Protocol defines a basic method for communication over the Internet. This protocol enables simple and reliable data exchange between 2 computers.

## 2. Protocol Description

### 2.1 Data Format

Data is transmitted in a binary format. Each message consists of a header followed by a payload.

### 2.2 Message Structure

Each message follows this structure:

- **Header**:
  - **Header Byte**: Indicates the start of the header (`0x8E`)
  - **Message Type**: Specifies the type of message (e.g., `0x80` for data message).

- **Payload**: Actual data to be transmitted.
    - **Payload Byte**: Indicates the start of the payload (`0x8D`)
    - **Payload Data**: Actual data to be transmitted.
    - **Checksum Byte**: The checksum of the payload. (Note: this is not including the checksum byte.)
    - **End Byte**: Indicates the end of the payload (`0x8F`)

### 2.3 Supported Commands

| **Command** | **Description** | **Byte Code** |
|---|---|---|
| **Data Message** | Used for transmitting data (from device to host) resembling "received" data from the modem. | `0x80` |
| **DtD Settings Agreement** | Agreeing on settings so that smooth data transfer can occur | `0x81` |
| **Saved for more data types**| Saved for future use | `0x82 - 0x85` |
| **Acknowledgement** | Acknowledges receipt of a message. (sent in DtD message) | `0x86` |
| **NAK** | Not Acknowledged. Indicates that the message was not received. (sent in DtD message) | `0x87` |
| **Abort** | Aborts the current transmission. (sent in DtD message) | `0x88` |
| **Busy** | Busy. Indicates that the modem is busy. (sent in DtD message) | `0x89` |
| **Error** | Indicates that an error has occurred. (sent in DtD message) | `0x8A` |
| **Ignore** | Ignores the next Command code (Allows for extended alphabets to not interfere with the transfer protocol) (sent in DtD message) | `0x8B` |
| **Search Ping** | Used to search for a device. (Only exception for sending messages, sent alone without the default structure) | `0x8C` |
| **Start Of Payload** | Indicates the start of the payload. | `0x8D` |
| **Header**| Indicates the start of the header. | `0x8E` |
| **End Of Payload** | Indicates the end of the payload. | `0x8F` |
| **Keep Alive Call** | A message to make sure that the other device doesn't disconnect| `0x90` |
| **Saved for more commands**| Saved for future use | `0x91 - 0xBF` |

## 3. Protocol Implementation

### 3.1 Device Initialization

1. Configure Internet connectivity.
2. Implement endpoint handlers for data transmission/reception.

### 3.2 Message Handling

1. Parse incoming messages based on the defined message structure.
2. Process received data based on message type.

### 3.3 Message Format

- **Data Message**:
  - **Header**: `0xAA 0x01 <Payload Length>`
  - **Payload**: Variable-length data bytes.

### 3.4 Error Handling

Error handling mechanisms are crucial for ensuring the reliability and robustness of the protocol. The following strategies and implementations are employed:

#### 3.4.1 Timeout Mechanism

Every seccond a Keep Alive Call (KAC) is sent and if the other dvice doesn't send another KAC call within a seccond send an Abort Call and close the connection.

#### 3.4.2 Checksum Verification

To ensure data integrity, a checksum can be calculated and transmitted alongside each message. The receiver verifies the checksum to detect transmission errors.

**Implementation**:
- Include a the checksum in the message footer.
- Calculate the checksum over the message payload and compare it with the received checksum.
- The calculation is: `length(payload)%256`
- If the checksums do not match, consider the message corrupted and request retransmission.

#### 3.4.3 NAK (Negative Acknowledgment) and Retransmission

When a receiver detects an error in a received message, it sends a NAK signal (negative acknowledgment) to the sender, indicating that the message was received incorrectly.

**Implementation**:
- Define a NAK response to indicate unsuccessful message reception.
- Upon receiving a NAK, the sender can retransmit the message or take appropriate corrective actions.

#### 3.4.4 Flow Control

Implement flow control mechanisms to manage data flow and prevent buffer overflow or underflow conditions.

**Implementation**:
- Use buffer management techniques to control the amount of data transmitted and received.
- Implement protocols such as XON/XOFF or hardware-based flow control (e.g., RTS/CTS) to regulate data flow between sender and receiver.

#### 3.4.5 Error Reporting and Recovery

Provide mechanisms for reporting errors and recovering from error states to maintain communication integrity.

**Implementation**:
- Define error codes and error handling procedures in the protocol specification.
- Implement error recovery strategies (e.g., retransmission, reset) based on specific error conditions encountered during communication.

#### 3.4.6 State Management

Maintain clear state management to handle transitions between communication states (e.g., idle, transmitting, receiving) and ensure proper error recovery based on the current state.

**Implementation**:
- Define a finite state machine (FSM) to manage communication states and transitions.
- Implement error recovery routines within each state to handle unexpected events and maintain protocol stability.

### 3.5 Example Error Scenarios

#### The payload is the wrong size
* The payload is the wrong size, and the receiver does not receive the expected number of bytes.
* The client or server sends an Error (`0x8A`)
* The sender re-sends the message.

**Examples**:
1. Timeout error due to data not being received within a specified duration.
2. Checksum mismatch indicating data corruption.
3. NAK response triggering message retransmission.

## 4. Example Usage

### 4.1 Sending Data (Device to Host)

1. Construct a data message resembling "received" data from the modem.
2. Send the message via Internet connectivity.

### 4.2 Receiving Data (Host to Device)

1. Poll for incoming data resembling "transmitted" data to the modem.
2. Parse and process received messages.

## 5. Security

* Some encryption may be added but is not required by the protocall.

## 6. Dependencies

- **Hardware**: Internet-capable microcontroller or Internet-connected device.
- **Firmware**: Network stack/library supporting data transfer over the Internet.
- **Host Application**: Software on the host for sending/receiving data.

## 7. Conclusion

This documentation provides a guideline for implementing and using the WModem Data Transfer Protocol for emulating a modem-like data transfer interface over the Internet. Refer to this documentation for protocol details and integration instructions.


#### Note: this documentation is under the `MIT License`