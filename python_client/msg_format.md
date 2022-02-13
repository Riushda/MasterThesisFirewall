# Message format

This document explains the format of the different messages sent to kernel. Each message follows the abstract format code + data, code is the message type and data is the payload associated with the message. Memory representation is always little endian unless specified. 

For the notations, [x:y] means from byte x to byte y included and brackets mean optional.

## Structures

### Member

    Description:
        It is the representation of a member inside the network.

    Size: Always 8 bytes

    Content:
    - [0:3] -> IP in big endian
    - [4:4] -> bitmask
    - [5:6] -> port in big endian
    - [7:7] -> negation of the port
        Value: [0, 1] for no or yes

### Rule

    Description:
        It is the representation of a traditional network layer rule.

    Size: Always 19 bytes

    Content:
    - [0:7] -> source member structure
    - [8:15] -> destination member structure
    - [16:16] -> policy
        Value: [0, 1] for deny/allow.
    - [17:18] -> the index where the rule should be inserted

### Value

    Description:
        A value is some data attached to a constraint, they differ depending on the type.

    Size: Variable

    Types:
        Subject: 
            This type has no value since the value is contained inside the field name.
        Int:
            A value of type int is always an interval, thus the size is always 8 bytes (for two integers).
        Str:
            A value of type str is encoded as the length (1 byte) followed by the string. So, the total length 
            is 1 + the size of the string.
            
### Constraint

    Description:
        A constraint which applies to a specific context. It can be either time, subject, int or str.

    Size: Variable

    Content:
    - [0:0] -> type
        Value: [0, 1, 2] for subject, int and str.
    - [1:1] -> field len (l), max 255
    - [2:(l + 1)] -> field name
    - [(l + 2):(l + 2)] -> number of values, max 255
    - [(l + 3):n] -> a sequence of value structures

### Relation

    Description:
        It is the representation of a context-based rule. A relation is either one or two rules (depending on the presence of a broker) followed by a context. The context can be empty or a sequence of constraints. It is in fact always empty for non-contextual rules.

    Size: Variable

    Content with broker:
    - [0:0] -> has_broker, always 0 for non-contextual rules
        Value: [0, 1] depending on the presence of a broker
    -[1:19] -> first rule structure
    -{[20:38] -> second rule structure, if has_broker is 1}
    -[39:39] -> number of constraints, max 255
    -{[40:n] -> a sequence of constraint structures}

    Content without broker:
    - [0:0] -> has_broker, always 0 for non-contextual rules
        Value: [0, 1] depending on the presence of a broker
    -[1:19] -> first rule structure
    -[20:20] -> number of constraints, max 255
    -{[21:n] -> a sequence of constraint structures}

## Messages

### Pid

    Description: 
        Sends the pid of the client to the firewall. 

    Usage: 
        This is used only once when the daemon starts.

    Size: Always 7 bytes

    Content:
        - [0:1] -> length of the message
        - [2:2] -> code PID with value 0
        - [3:6] -> the pid 

### Add relation 

    Description: 
        Adds a relation inside the firewall. 

    Usage: 
        This is used both to add contextual rules and non contextual rules, there is no "add rule".

    Size: Variable

    Content:
        - [0:1] -> length of the message
        - [2:2] -> code ADD_RELATION with value 1
        - [3:n] -> relation structure

### Remove relation 

    Description: 
        Removes a relation inside the firewall. 

    Usage: 
        This is used both to remove contextual rules and non contextual rules, there is no "remove rule". If has_broker is true then
        both the specified rule and the following rule should be deleted.

    Size: Always 6 bytes

    Content:
        - [0:1] -> length of the message
        - [2:2] -> code RM_RELATION with value 2
        - [3:3] -> has_broker, always 0 for non-contextual rules
            Value: [0, 1] depending on the presence of a broker
        - [4:22] -> first rule structure
        - {[23:41] -> second rule structure}

### Enable relation 

    Description: 
        Activates a relation inside the firewall. 

    Usage: 
        This is used for dynamic context such as time to dynamically activate a relation. If has_broker is true then
        both the specified rule and the following rule should be enabled.

    Size: Always 6 bytes

    Content:
        - [0:1] -> length of the message
        - [2:2] -> code ENABLE_RELATION with value 3
        - [3:3] -> has_broker, always 0 for non-contextual rules
            Value: [0, 1] depending on the presence of a broker
        - [4:5] -> index of the first rule
  
### Disable relation 

    Description: 
        Deactivates a relation inside the firewall. 

    Usage: 
        This is used for dynamic context such as time to dynamically deactivate a relation. If has_broker is true then
        both the specified rule and the following rule should be disabled.
    
    Size: Always 6 bytes

    Content:
        - [0:1] -> length of the message
        - [2:2] -> code DISABLE_RELATION with value 4
        - [3:3] -> has_broker, always 0 for non-contextual rules
            Value: [0, 1] depending on the presence of a broker
        - [4:5] -> index of the first rule
