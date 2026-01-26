export interface JointState {
  timestamp: number; // seconds since epoch (float)
  joints: Record<string, number>; // bone_name -> rotation (radians)
}

export type JointName = string

export interface JointProfileEntry {
  boneName: string;
  axis?: 'x' | 'y' | 'z'; // preferred rotation axis (default 'x')
  zeroOffset?: number; // radians to add to incoming value
  min?: number; // min radians
  max?: number; // max radians
}

export interface JointProfile {
  [joint: string]: JointProfileEntry
}

export const DEFAULT_JOINTS = [
  'wrist_yaw',
  'thumb_mcp',
  'thumb_ip',
  'index_mcp',
  'index_pip',
  'index_dip',
  'middle_mcp',
  'middle_pip',
  'middle_dip',
  'ring_mcp',
  'ring_pip',
  'ring_dip',
  'pinky_mcp',
  'pinky_pip',
  'pinky_dip',
]
