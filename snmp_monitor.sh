#!/bin/bash

HOSTS="192.168.240.240" 
COMMUNITY="public"
VERSION="2c"

LOGFILE="snmp_parser/snmp_log"

is_number() {
    [[ $1 =~ ^[0-9]+$ ]]
}

while true; do
    TIMESTAMP=$(date '+%F %T.%3N')

    OUTPUTS=()

    for HOST in "${HOSTS[@]}"; do
        # CPU Load 5 phút
        CPU_LOADS=$(snmpwalk -v$VERSION -c $COMMUNITY $HOST 1.3.6.1.4.1.9.9.109.1.1.1.1.8 2>/dev/null | awk '{print $NF}' | paste -sd "," -)
        CPU_LOADS=${CPU_LOADS:-N/A}

        # RAM Usage (%)
        MEM_USED=$(snmpwalk -v$VERSION -c $COMMUNITY $HOST 1.3.6.1.4.1.9.9.48.1.1.1.6 2>/dev/null | awk '{print $NF}' | grep -Eo '^[0-9]+' | paste -sd+ - | bc 2>/dev/null)
        MEM_FREE=$(snmpwalk -v$VERSION -c $COMMUNITY $HOST 1.3.6.1.4.1.9.9.48.1.1.1.5 2>/dev/null | awk '{print $NF}' | grep -Eo '^[0-9]+' | paste -sd+ - | bc 2>/dev/null)
        MEM_USED=${MEM_USED:-0}
        MEM_FREE=${MEM_FREE:-0}
        MEM_TOTAL=$((MEM_USED + MEM_FREE))
        MEM_USAGE=0
        if [ "$MEM_TOTAL" -gt 0 ]; then
            MEM_USAGE=$((MEM_USED * 100 / MEM_TOTAL))
        fi

        # Temperature sensors
        TEMPS=$(snmpwalk -v$VERSION -c $COMMUNITY $HOST 1.3.6.1.4.1.9.9.13.1.3.1.3 2>/dev/null | awk '{print $NF}' | grep -Eo '^[0-9]+' | paste -sd "," -)
        TEMPS=${TEMPS:-N/A}

        # Interface bandwidth (active ports)
        ACTIVE_IFINDEXES=$(snmpwalk -v$VERSION -c $COMMUNITY $HOST 1.3.6.1.2.1.2.2.1.8 2>/dev/null | grep "INTEGER: 1" | awk -F '.' '{print $NF}' | awk '{print $1}')

        IF_BANDWIDTH=()
        for IFINDEX in $ACTIVE_IFINDEXES; do
            DESC=$(snmpget -v$VERSION -c $COMMUNITY $HOST 1.3.6.1.2.1.2.2.1.2.$IFINDEX -Oqv 2>/dev/null)
            IN_OCT=$(snmpget -v$VERSION -c $COMMUNITY $HOST 1.3.6.1.2.1.31.1.1.1.6.$IFINDEX -Oqv 2>/dev/null)
            OUT_OCT=$(snmpget -v$VERSION -c $COMMUNITY $HOST 1.3.6.1.2.1.31.1.1.1.10.$IFINDEX -Oqv 2>/dev/null)
            SPEED=$(snmpget -v$VERSION -c $COMMUNITY $HOST 1.3.6.1.2.1.31.1.1.1.15.$IFINDEX -Oqv 2>/dev/null)

            DESC=${DESC:-N/A}
            if is_number "$IN_OCT"; then
                IN_KB=$((IN_OCT / 1024))
            else
                IN_KB=0
            fi
            if is_number "$OUT_OCT"; then
                OUT_KB=$((OUT_OCT / 1024))
            else
                OUT_KB=0
            fi
            SPEED=${SPEED:-N/A}

            IF_BANDWIDTH+=("[$DESC] IN:${IN_KB}KB OUT:${OUT_KB}KB Speed:${SPEED}Mbps")
        done
        IF_BANDWIDTH_STR=$(IFS='; '; echo "${IF_BANDWIDTH[*]}")

        # Gom dữ liệu host thành 1 phần
        HOST_DATA="CPU=$CPU_LOADS% Mem=$MEM_USAGE% Temp=[$TEMPS] IF=\"$IF_BANDWIDTH_STR\""
        OUTPUTS+=("$HOST_DATA")
    done

    # Ghép tất cả host trên 1 dòng
    LINE="$TIMESTAMP level=INFO $(
        IFS=' | '; echo "${OUTPUTS[*]}"
    )"

    echo "$LINE" >> $LOGFILE

    sleep 30
done
