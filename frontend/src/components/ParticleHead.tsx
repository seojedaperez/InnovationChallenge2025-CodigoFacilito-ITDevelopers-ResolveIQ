import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';

const ParticleHead: React.FC = () => {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        let camera: THREE.PerspectiveCamera;
        let scene: THREE.Scene;
        let renderer: THREE.WebGLRenderer;
        let particles: THREE.Points;
        let mouseX = 0;
        let mouseY = 0;
        let windowHalfX = window.innerWidth / 2;
        let windowHalfY = window.innerHeight / 2;
        let animationId: number;

        const init = () => {
            const container = containerRef.current;
            if (!container) return;

            // Camera
            camera = new THREE.PerspectiveCamera(35, window.innerWidth / window.innerHeight, 1, 2000);
            camera.position.z = 300;

            // Scene
            scene = new THREE.Scene();

            // Manager
            const manager = new THREE.LoadingManager();

            // Material
            const p_material = new THREE.PointsMaterial({
                color: 0xFFFFFF,
                size: 1.5,
                sizeAttenuation: true
            });

            // Loader
            const loader = new OBJLoader(manager);
            loader.load('https://s3-us-west-2.amazonaws.com/s.cdpn.io/40480/head.obj', (object) => {
                const positions: number[] = [];
                const scale = 8;

                object.traverse((child) => {
                    if (child instanceof THREE.Mesh) {
                        const geometry = child.geometry;

                        // Handle BufferGeometry (newer Three.js)
                        if (geometry.isBufferGeometry) {
                            const positionAttribute = geometry.attributes.position;
                            for (let i = 0; i < positionAttribute.count; i++) {
                                const x = positionAttribute.getX(i);
                                const y = positionAttribute.getY(i);
                                const z = positionAttribute.getZ(i);
                                positions.push(x * scale, y * scale, z * scale);
                            }
                        }
                    }
                });

                const geometry = new THREE.BufferGeometry();
                geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
                geometry.center(); // Center the geometry

                particles = new THREE.Points(geometry, p_material);
                scene.add(particles);
            });

            // Renderer
            renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setClearColor(0x000000, 0);
            container.appendChild(renderer.domElement);

            // Events
            document.addEventListener('mousemove', onDocumentMouseMove);
            window.addEventListener('resize', onWindowResize);
        };

        const onWindowResize = () => {
            windowHalfX = window.innerWidth / 2;
            windowHalfY = window.innerHeight / 2;
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        };

        const onDocumentMouseMove = (event: MouseEvent) => {
            mouseX = (event.clientX - windowHalfX) / 2;
            mouseY = (event.clientY - windowHalfY) / 2;
        };

        const animate = () => {
            animationId = requestAnimationFrame(animate);
            render();
        };

        const render = () => {
            if (!particles) return;

            camera.position.x += ((mouseX * 0.5) - camera.position.x) * 0.05;
            camera.position.y += (-(mouseY * 0.5) - camera.position.y) * 0.05;
            camera.lookAt(scene.position);

            renderer.render(scene, camera);
        };

        init();
        animate();

        return () => {
            cancelAnimationFrame(animationId);
            document.removeEventListener('mousemove', onDocumentMouseMove);
            window.removeEventListener('resize', onWindowResize);
            if (containerRef.current && renderer) {
                containerRef.current.removeChild(renderer.domElement);
            }
            if (renderer) renderer.dispose();
        };
    }, []);

    return (
        <div
            ref={containerRef}
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                zIndex: 0,
                pointerEvents: 'none' // Allow clicks to pass through
            }}
        />
    );
};

export default ParticleHead;
