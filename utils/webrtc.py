"""WebRTC utilities and helpers."""
import re
from aiortc import RTCPeerConnection, RTCConfiguration, RTCIceServer
from aiortc.rtcicetransport import RTCIceCandidate
import config


def create_rtc_configuration() -> RTCConfiguration:
    """Create RTCConfiguration with STUN servers."""
    return RTCConfiguration(
        iceServers=[RTCIceServer(urls=[url]) for url in config.STUN_SERVERS]
    )


def parse_ice_candidate(candidate_data: dict) -> RTCIceCandidate:
    """
    Parse ICE candidate from client data.
    
    Args:
        candidate_data: Dictionary containing candidate information
        
    Returns:
        RTCIceCandidate object or None if parsing fails
    """
    if not candidate_data or "candidate" not in candidate_data:
        return None
    
    sdp = candidate_data["candidate"]
    
    # Parse ICE candidate SDP string
    match = re.match(
        r"candidate:(\S+) (\d+) (\S+) (\d+) (\S+) (\d+) typ (\S+)(?: raddr (\S+) rport (\d+))?",
        sdp,
    )
    
    if not match:
        print(f"⚠️ Could not parse ICE candidate: {sdp}")
        return None
    
    foundation, component, protocol, priority, ip, port, type_, raddr, rport = match.groups()
    
    return RTCIceCandidate(
        foundation=foundation,
        component=int(component),
        priority=int(priority),
        ip=ip,
        protocol=protocol,
        port=int(port),
        type=type_,
        relatedAddress=raddr,
        relatedPort=int(rport) if rport else None,
        sdpMid=candidate_data.get("sdpMid"),
        sdpMLineIndex=candidate_data.get("sdpMLineIndex"),
    )