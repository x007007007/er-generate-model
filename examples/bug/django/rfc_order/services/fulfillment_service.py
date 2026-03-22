"""
订单履约服务
根据 sell_item.category 分发不同的履约逻辑：
- PACKAGE → 创建单张套餐兑换券（用户到线下商户兑换实物，实物含激活码+NFC）
- ADD_ON  → 按 order_item 展开，根据 activation_mode 创建 entitlement + voucher
"""
import logging
import uuid
from datetime import datetime
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


def process_order_paid(order):
    """
    处理订单支付成功后的履约逻辑

    根据 sell_item.category 分发:
    - PACKAGE: 创建单张兑换券 → 用户到线下商户兑换实物（实物含激活码+NFC）
              → 用户扫描激活码 → grant_activation_code_bundle_entitlements 自动发放子权益
    - ADD_ON:  按 order_item 展开 → 根据 activation_mode 创建 entitlement + voucher

    Args:
        order: OrderModel 实例
    """
    logger.info(f"Processing fulfillment for order {order.pk}")

    sell_item = order.sell_item
    category = sell_item.category or 'ADD_ON'

    logger.info(f"Order {order.pk} category: {category}")

    if category == 'PACKAGE':
        _process_package_order(order)
    elif category == 'ADD_ON':
        _process_addon_order(order)
    else:
        logger.warning(f"Unknown category: {category} for order {order.pk}")


def _process_package_order(order):
    """
    处理 PACKAGE（套餐包）订单

    核心流程:
    1. 创建一条 entitlement(PENDING) 关联套餐 sell_item（代表"可兑换实物包裹"）
    2. 创建一张 voucher(REDEEM) 兑换码
    3. 发送兑换码到邮箱

    后续流程（不在此函数内）:
    - 用户到线下商户出示兑换码 → POS 核销 → entitlement PENDING → USED_UP
    - 用户获得实物（含激活码+NFC）→ 扫描激活码 → grant_activation_code_bundle_entitlements 创建子权益
    """
    from kinkotech.rfc_backend.domains.rfc_order.models import (
        EntitlementModel,
        VoucherModel,
    )

    logger.info(f"Processing package order {order.pk}")

    with transaction.atomic():
        # 1. 创建包裹级 entitlement（代表"可兑换实物"）
        entitlement = EntitlementModel.objects.create(
            visitor=order.visitor,
            sell_item=order.sell_item,
            status='PENDING',
            order=order,
            meta={'fulfillment_type': 'package_pickup'},
        )

        # 2. 创建单张兑换码
        voucher_code = _generate_voucher_code()
        voucher = VoucherModel.objects.create(
            entitlement=entitlement,
            order=order,
            voucher_type='REDEEM',
            sell_item=order.sell_item,
            issued_seq=1,
            code=voucher_code,
            meta={'fulfillment_type': 'package_pickup'},
        )

        logger.info(
            f"Created package entitlement {entitlement.pk} and voucher {voucher.code} "
            f"for order {order.pk}"
        )

    # 3. 发送邮件
    if order.email:
        try:
            from kinkotech.rfc_backend.infrastructure.email.email_service import send_voucher_email
            send_voucher_email(
                email=order.email,
                vouchers=[voucher],
                order_id=order.pk,
            )
            logger.info(f"Package voucher email sent to {order.email}")
        except Exception as e:
            logger.error(f"Error sending package voucher email: {e}")


def _process_addon_order(order):
    """
    处理 ADD_ON（附加项/单品）订单
    按 order_item 展开，根据每个 sell_item 的 activation_mode 创建对应的 entitlement + voucher:
    - REDEEM_REQUIRED: 创建 entitlement(PENDING) + voucher(REDEEM)
    - IMMEDIATE: 创建 entitlement(ACTIVE)，不生成 voucher
    """
    from kinkotech.rfc_backend.domains.rfc_order.models import (
        OrderItemModel,
        EntitlementModel,
        VoucherModel,
    )

    logger.info(f"Processing add-on order {order.pk}")

    # 1. 获取订单行
    order_items = OrderItemModel.objects.filter(order=order).select_related('sell_item')

    if not order_items.exists():
        # 如果没有订单行, 创建一条（兼容旧数据）
        order_items = [OrderItemModel.objects.create(
            order=order,
            sell_item=order.sell_item,
            qty=1,
            unit_amount=order.amount,
            amount=order.amount,
        )]

    # 2. 为每个订单行创建权益和券
    vouchers_created = []

    for order_item in order_items:
        activation_mode = order_item.sell_item.activation_mode or 'REDEEM_REQUIRED'

        for i in range(order_item.qty):
            if activation_mode == 'IMMEDIATE':
                # 立即生效（如记忆胶囊），不生成 voucher
                entitlement = EntitlementModel.objects.create(
                    visitor=order.visitor,
                    sell_item=order_item.sell_item,
                    status='ACTIVE',
                    order=order,
                    order_item=order_item,
                    meta={},
                )
                logger.info(f"Created active entitlement {entitlement.pk} "
                           f"for order_item {order_item.pk}")
            else:
                # REDEEM_REQUIRED（默认）：创建 PENDING + voucher
                entitlement = EntitlementModel.objects.create(
                    visitor=order.visitor,
                    sell_item=order_item.sell_item,
                    status='PENDING',
                    order=order,
                    order_item=order_item,
                    meta={},
                )

                voucher_code = _generate_voucher_code()
                voucher = VoucherModel.objects.create(
                    entitlement=entitlement,
                    order=order,
                    order_item=order_item,
                    voucher_type='REDEEM',
                    sell_item=order_item.sell_item,
                    issued_seq=i + 1,
                    code=voucher_code,
                    meta={},
                )

                vouchers_created.append(voucher)
                logger.info(f"Created entitlement {entitlement.pk} and voucher {voucher.code} "
                           f"for order_item {order_item.pk}")

    # 3. 发送邮件
    if order.email and vouchers_created:
        try:
            from kinkotech.rfc_backend.infrastructure.email.email_service import send_voucher_email
            send_voucher_email(
                email=order.email,
                vouchers=vouchers_created,
                order_id=order.pk,
            )
            logger.info(f"Voucher email sent to {order.email}")
        except Exception as e:
            logger.error(f"Error sending voucher email: {e}")


def _generate_voucher_code() -> str:
    """
    生成券码
    格式: V + 时间戳(8位) + 随机UUID(8位)
    """
    timestamp = datetime.now().strftime('%Y%m%d')
    random_part = str(uuid.uuid4()).replace('-', '')[:8].upper()
    return f"V{timestamp}{random_part}"


def create_challenge_reward(visitor, challenge, sell_item):
    """
    创建挑战奖励
    挑战完成时调用,创建entitlement(PENDING, challenge_id) + voucher(CHALLENGE_PRIZE)

    Args:
        visitor: VisitorModel实例
        challenge: ChallengeModel实例
        sell_item: SellItemModel实例(奖励对应的售卖项)

    Returns:
        (entitlement, voucher) tuple
    """
    from kinkotech.rfc_backend.domains.rfc_order.models import (
        EntitlementModel,
        VoucherModel,
    )

    logger.info(f"Creating challenge reward for visitor {visitor.pk}, challenge {challenge.pk}")

    # 创建权益
    entitlement = EntitlementModel.objects.create(
        visitor=visitor,
        sell_item=sell_item,
        status='PENDING',
        challenge=challenge,
        meta={'reward_type': 'challenge'},
    )

    # 创建券
    voucher_code = _generate_voucher_code()
    voucher = VoucherModel.objects.create(
        entitlement=entitlement,
        voucher_type='CHALLENGE_PRIZE',
        sell_item=sell_item,
        code=voucher_code,
        meta={'challenge_id': challenge.pk},
    )

    logger.info(f"Created challenge reward: entitlement {entitlement.pk}, voucher {voucher.code}")

    return entitlement, voucher


def grant_activation_code_bundle_entitlements(visitor, activation_code):
    """
    激活码扫码时，自动发放 bundle_sell_item 绑定的套餐权益

    核心逻辑：
    - 若 activation_code.bundle_sell_item 存在，则按套餐的 bundle_item 展开
    - 为每个子商品根据 activation_mode 创建对应的 entitlement（+ voucher）
    - 若 bundle_sell_item 不存在（非套餐激活码），则跳过

    Args:
        visitor: VisitorModel 实例（已绑定 activation_code 的正式用户）
        activation_code: ActivationCodeModel 实例

    Returns:
        list: 创建的 (entitlement, voucher) tuple 列表；空列表表示无 bundle
    """
    from kinkotech.rfc_backend.domains.rfc_order.models import (
        EntitlementModel,
        VoucherModel,
        SellItemBundleItemModel,
    )

    bundle_sell_item = activation_code.bundle_sell_item
    if not bundle_sell_item:
        logger.info(f"Activation code {activation_code.pk} has no bundle_sell_item, skip entitlement grant")
        return []

    logger.info(f"Granting bundle entitlements for visitor {visitor.pk}, "
                f"activation_code {activation_code.pk}, bundle {bundle_sell_item.code}")

    results = []

    if bundle_sell_item.is_bundle:
        # 套餐：按 bundle_item 展开
        bundle_items = SellItemBundleItemModel.objects.filter(
            bundle_sell_item=bundle_sell_item,
        ).select_related('component_sell_item')

        for bundle_item in bundle_items:
            component = bundle_item.component_sell_item
            activation_mode = component.activation_mode or 'REDEEM_REQUIRED'

            for i in range(bundle_item.qty):
                if activation_mode == 'IMMEDIATE':
                    # 立即生效（如记忆胶囊），不生成 voucher
                    entitlement = EntitlementModel.objects.create(
                        visitor=visitor,
                        sell_item=component,
                        status='ACTIVE',
                        meta={'source': 'activation_code_bundle', 'activation_code_id': activation_code.pk},
                    )
                    results.append((entitlement, None))
                else:
                    # REDEEM_REQUIRED（默认）：PENDING + voucher
                    entitlement = EntitlementModel.objects.create(
                        visitor=visitor,
                        sell_item=component,
                        status='PENDING',
                        meta={'source': 'activation_code_bundle', 'activation_code_id': activation_code.pk},
                    )

                    voucher_code = _generate_voucher_code()
                    voucher = VoucherModel.objects.create(
                        entitlement=entitlement,
                        voucher_type='REDEEM',
                        sell_item=component,
                        issued_seq=i + 1,
                        code=voucher_code,
                        meta={'source': 'activation_code_bundle'},
                    )
                    results.append((entitlement, voucher))

                logger.info(f"Granted entitlement {entitlement.pk} for component {component.code}")
    else:
        # 单品：直接创建
        activation_mode = bundle_sell_item.activation_mode or 'REDEEM_REQUIRED'

        if activation_mode == 'IMMEDIATE':
            entitlement = EntitlementModel.objects.create(
                visitor=visitor,
                sell_item=bundle_sell_item,
                status='ACTIVE',
                meta={'source': 'activation_code_bundle', 'activation_code_id': activation_code.pk},
            )
            results.append((entitlement, None))
        else:
            entitlement = EntitlementModel.objects.create(
                visitor=visitor,
                sell_item=bundle_sell_item,
                status='PENDING',
                meta={'source': 'activation_code_bundle', 'activation_code_id': activation_code.pk},
            )

            voucher_code = _generate_voucher_code()
            voucher = VoucherModel.objects.create(
                entitlement=entitlement,
                voucher_type='REDEEM',
                sell_item=bundle_sell_item,
                issued_seq=1,
                code=voucher_code,
                meta={'source': 'activation_code_bundle'},
            )
            results.append((entitlement, voucher))

    logger.info(f"Total {len(results)} entitlements granted for activation code bundle")
    return results
