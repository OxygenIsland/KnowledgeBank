在 Unity 中，创建逼真的角色控制和移动是许多游戏项目的核心需求。Character Controller 组件提供了一种简单而强大的方式来实现这些功能，相比 Rigidbody，Character Controller 提供了更高的控制灵活性，尤其适合需要精准移动和跳跃的角色。它允许开发者为角色添加碰撞检测、自动斜坡行走和复杂的移动控制。
![[Pasted image 20241017175648.png|500]]

## 🔨 Character Controller 的核心特性
1. 碰撞检测与响应
		Character Controller 自动处理与环境的碰撞，包括斜坡行走和楼梯上下。
2. 移动控制
		开发者可以通过代码精确控制角色的移动，包括速度、方向和跳跃。
3. 定制化
		可以调整各种参数，如移动速度、跳跃高度和碰撞半径，以适应不同的游戏风格。
4. 支持多层
		Character Controller 支持多层碰撞，使得角色可以在复杂的游戏环境中自由移动。
## 示例代码
### 示例1：角色移动与跳跃
```csharp
using UnityEngine;

[RequireComponent(typeof(CharacterController))]
public class PlayerController : MonoBehaviour
{
    public float moveSpeed = 5f; // 角色移动速度
    public float jumpHeight = 2f; // 跳跃高度
    public float gravity = -9.81f; // 重力
    private CharacterController controller;
    private Vector3 velocity;
    private bool isGrounded;

    void Start()
    {
        // 获取角色的 Character Controller 组件
        controller = GetComponent<CharacterController>();
    }
    void Update()
    {
        // 检测角色是否在地面上
        isGrounded = controller.isGrounded;
        if (isGrounded && velocity.y < 0)
        {
            velocity.y = -2f; // 当角色在地面时，重置垂直速度
        }
        // 获取水平移动输入（WASD 或方向键）
        float moveX = Input.GetAxis("Horizontal");
        float moveZ = Input.GetAxis("Vertical");
        // 根据输入计算角色的移动方向
        Vector3 move = transform.right * moveX + transform.forward * moveZ;
        // 通过 Character Controller 移动角色
        controller.Move(move * moveSpeed * Time.deltaTime);
        // 跳跃处理
        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            // 使用公式计算跳跃的垂直速度：v = sqrt(h * -2 * g)
            velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
        }
        // 应用重力
        velocity.y += gravity * Time.deltaTime;
        // 垂直方向上的移动（重力和跳跃）
        controller.Move(velocity * Time.deltaTime);
    }
}
```
**代码解析**
1. CharacterController controller：获取 Character Controller 组件，用于控制角色的移动。
2. IsGrounded = controller. IsGrounded：检测角色是否接触地面，用于处理跳跃和重力逻辑。
3. Input.GetAxis ("Horizontal") 和 Input.GetAxis ("Vertical")：获取玩家的输入，用于控制角色在 X 和 Z 方向上的移动。
4. Controller.Move ()：通过 Character Controller 的 Move () 方法实现角色的移动。
5. 跳跃：通过 Input.GetButtonDown ("Jump") 检测跳跃按键，并使用物理公式计算跳跃速度。
6. 重力：通过持续减少 velocity. Y 模拟重力，并使角色下落。
### 示例2：使用鼠标控制角色视角
```csharp
public class MouseLook : MonoBehaviour
{
    public float mouseSensitivity = 100f; // 鼠标灵敏度
    public Transform playerBody; // 角色的 Transform
    private float xRotation = 0f;
    void Start()
    {
        // 锁定鼠标，使其不可见并保持在屏幕中央
        Cursor.lockState = CursorLockMode.Locked;
    }
    void Update()
    {
        // 获取鼠标移动输入
        float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity * Time.deltaTime;
        float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity * Time.deltaTime;
        // 计算视角上下旋转，限制最大和最小角度
        xRotation -= mouseY;
        xRotation = Mathf.Clamp(xRotation, -90f, 90f);
        // 旋转摄像机的视角
        transform.localRotation = Quaternion.Euler(xRotation, 0f, 0f);
        // 控制角色左右旋转
        playerBody.Rotate(Vector3.up * mouseX);
    }
}
```
在这个例子中，MouseLook 脚本用于处理摄像机的旋转。它允许玩家通过鼠标控制视角，角色则会根据鼠标的左右移动进行旋转。

Cursor. LockState = CursorLockMode. Locked：锁定鼠标位置，使其保持在屏幕中央。
PlayerBody.Rotate (Vector 3. Up * mouseX)：通过旋转角色的 Y 轴来实现左右旋转。
## CharacterController 会与碰撞体发生作用吗？
