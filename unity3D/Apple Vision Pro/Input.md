There are two ways to capture user intent on visionOS: 3D touch and skeletal hand tracking. ==In exclusive mode, developers can also access head tracking data.==
## 3D Touch and TouchSpace
In both bounded and unbounded volumes, a 3D touch input is provided when the user looks at an ==object with an input collider==  and performs the “pinch” (touch thumb and index finger together to “**tap**” or “**drag**”) gesture. The **SpatialPointerDevice Input device** provides that information to the developer. If the user holds the pinch gesture, a drag is initiated and the application is provided “move” updates relative to the original start point. 
3D touch events are exposed via the **SpatialPointerDevice Input device**, which is built on top of the `com.unity.inputsystem` package, otherwise known as the New Input System. Existing actions bound to a touchscreen device should work for 2D input. ====For 3D input, users can bind actions to the specific **SpatialPointerDevice** device for a 3D position vector.====
A collider with the collision mask set to the PolySpatial Input layer is required on any object that can receive 3D touch events. Only touches against those events are reported. 

This input device has a VR counterpart called **VisionOSSpatialPointerDevice**. The primary difference between the two is that the interaction doesn't require colliders. Thus, **VisionOSSpatialPointerDevice** is missing input controls related to the interaction (`targetId`, `interactionPosition`, etc.).