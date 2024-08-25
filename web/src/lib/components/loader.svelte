<!--

https://github.com/n3r4zzurr0/svg-spinners

Frankenstein'd 90-ring-with-bg.svg and ring-resize.svg

=====

The MIT License (MIT)

Copyright (c) Utkarsh Verma

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

-->
<svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
    {...$$props}
>
    <path
        d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z"
        opacity=".25"
    />

    <g>
        <circle
            cx="12"
            cy="12"
            r="9.5"
            fill="none"
            stroke-width="3"
            stroke-linecap="round"
        >
            <animate
                attributeName="stroke-dasharray"
                dur="1.5s"
                calcMode="spline"
                values="0 150;42 150;42 150;42 150"
                keyTimes="0;0.475;0.95;1"
                keySplines="0.42,0,0.58,1;0.42,0,0.58,1;0.42,0,0.58,1"
                repeatCount="indefinite"
            />
            <animate
                attributeName="stroke-dashoffset"
                dur="1.5s"
                calcMode="spline"
                values="0;-16;-59;-59"
                keyTimes="0;0.475;0.95;1"
                keySplines="0.42,0,0.58,1;0.42,0,0.58,1;0.42,0,0.58,1"
                repeatCount="indefinite"
            />
        </circle>
        <animateTransform
            attributeName="transform"
            type="rotate"
            dur="2s"
            values="0 12 12;360 12 12"
            repeatCount="indefinite"
        />
    </g>
</svg>
