import React from 'react';

interface WaqfLogoMarkProps {
  size?: number;
  className?: string;
}

export const WaqfLogoMark: React.FC<WaqfLogoMarkProps> = ({ size = 46, className }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 512 512"
      width={size}
      height={size}
      className={className}
      role="img"
      aria-label="WAQF DAO Medina Hisbah Vault Seal"
    >
      <defs>
        <radialGradient id="wdSealBg" cx="35%" cy="25%" r="80%">
          <stop offset="0%" stopColor="#13342B" />
          <stop offset="55%" stopColor="#0A1B16" />
          <stop offset="100%" stopColor="#06110E" />
        </radialGradient>
        <linearGradient id="wdSealGold" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#F5D993" />
          <stop offset="45%" stopColor="#D4A84F" />
          <stop offset="100%" stopColor="#9B7222" />
        </linearGradient>
        <linearGradient id="wdSealEmerald" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#48E5A8" />
          <stop offset="50%" stopColor="#1EB980" />
          <stop offset="100%" stopColor="#0D6E49" />
        </linearGradient>
      </defs>

      <rect x="16" y="16" width="480" height="480" rx="108" fill="url(#wdSealBg)" />
      <rect
        x="18"
        y="18"
        width="476"
        height="476"
        rx="106"
        fill="none"
        stroke="url(#wdSealGold)"
        strokeWidth="3.5"
        strokeOpacity="0.55"
      />
      <rect
        x="124"
        y="124"
        width="264"
        height="264"
        rx="14"
        fill="#081713"
        fillOpacity="0.72"
        stroke="url(#wdSealGold)"
        strokeWidth="7.5"
        strokeLinejoin="round"
      />
      <rect
        x="124"
        y="124"
        width="264"
        height="264"
        rx="14"
        fill="#081713"
        fillOpacity="0.65"
        stroke="url(#wdSealGold)"
        strokeWidth="7.5"
        strokeLinejoin="round"
        transform="rotate(45 256 256)"
      />
      <g fill="#ECC774">
        <circle cx="256" cy="69" r="5" />
        <circle cx="388" cy="124" r="5" />
        <circle cx="443" cy="256" r="5" />
        <circle cx="388" cy="388" r="5" />
        <circle cx="256" cy="443" r="5" />
        <circle cx="124" cy="388" r="5" />
        <circle cx="69" cy="256" r="5" />
        <circle cx="124" cy="124" r="5" />
      </g>
      <path
        d="M 184 358 L 184 256 C 184 204 218 173 256 146 C 294 173 328 204 328 256 L 328 358 Z"
        fill="#050F0C"
        stroke="url(#wdSealGold)"
        strokeWidth="6.5"
        strokeLinejoin="round"
      />
      <path d="M 256 178 L 286 208 L 256 238 L 226 208 Z" fill="url(#wdSealGold)" />
      <path d="M 256 190 L 274 208 L 256 226 L 238 208 Z" fill="url(#wdSealEmerald)" />
      <circle cx="256" cy="208" r="4.5" fill="#FAF7F0" />
      <path
        d="M 241 240 C 223 252 216 266 216 286 L 216 340"
        fill="none"
        stroke="#108458"
        strokeWidth="11"
        strokeLinecap="round"
      />
      <line
        x1="256"
        y1="246"
        x2="256"
        y2="342"
        stroke="url(#wdSealEmerald)"
        strokeWidth="14"
        strokeLinecap="round"
      />
      <path
        d="M 271 240 C 289 252 296 266 296 286 L 296 340"
        fill="none"
        stroke="url(#wdSealGold)"
        strokeWidth="11"
        strokeLinecap="round"
      />
      <line
        x1="170"
        y1="358"
        x2="342"
        y2="358"
        stroke="url(#wdSealGold)"
        strokeWidth="6.5"
        strokeLinecap="round"
      />
      <line
        x1="204"
        y1="374"
        x2="308"
        y2="374"
        stroke="#1EB980"
        strokeWidth="4"
        strokeLinecap="round"
      />
    </svg>
  );
};
