import pandas as pd
import numpy as np

def make_summary(datasets):
    summary = pd.DataFrame({},)
    summary['dataset_name'] = datasets.keys()
    summary['columns_names'] = [list(dataset.columns)
                                for dataset in datasets.values()]
    summary['rows_num'] = [dataset.shape[0] for dataset in datasets.values()]
    summary['cols_num'] = [dataset.shape[1] for dataset in datasets.values()]
    summary['total_duplicates'] = [dataset.duplicated().sum() 
                                   for dataset in datasets.values()]
    summary = summary.set_index(['dataset_name'])
    return summary


def display_summary(datasets):
    summary = make_summary(datasets)
    display(summary.style.background_gradient(cmap='Purples'))
    return None


### MERGING DFS
def removekey(d, key):
    """ Copy and return the dictionary d with the deleted element
    at key ."""
    r = dict(d)
    del r[key]
    return r


# Had to use the following because locals() seemed not to work with df?
def arguments():
        """Returns a tuple containing :
           - a dictionary of the calling function's
           named arguments, and ;
           - a list of calling function's unnamed
           positional arguments.
        """
        from inspect import getargvalues, stack
        posname, kwname, args = getargvalues(stack()[1][0])[-3:]
        posargs = args.pop(posname, [])
        args.update(args.pop(kwname, []))
        return args, posargs
    

def merge_and_display(left, right, on=None, how='left', validate=None):
    """ Merge from left and display nulls values and shapes 
    in order to understand what occurs during the merging process."""
    args, _ = arguments()
    df = pd.merge(**args)
    print(f"shape before merging : {left.shape}")
    print(f"shape of the right df: {right.shape}")
    print(f"shape after merging : {df.shape}")
    display(df.notnull().mean())
    return df

#### Checking prices consistency
def order_total_price(grp):
    """ search the price and the freight value of each item and sum it.
    
    remark : the min aggregate function, could be max or mean,
    it wont change the result."""
    return round(grp.groupby('order_item_id')[['price', 'freight_value']]
            .min().sum().sum(), 2)
    
    
def total_payment_value(grp):
    """ search the values for each sequential payment and sum it
    
    remark : the min aggregate function, could be max or mean,
    it wont change the result."""
    return round(grp.groupby('payment_sequential')['payment_value']
            .min().sum(), 2)
    
    
def is_total_price_equal_to_payment(grp):
    """ Check wether the payment and the total order price match.
    A 5 centavos difference is tolerated."""
    return (abs(total_payment_value(grp) - order_total_price(grp)) <= 0.05) 

def price_payment_diff(grp):
    """ Test if the order total price is not zero and if price and payment
    are different for more than 5 centavos."""
    return ((order_total_price(grp) != 0) 
            & ~is_total_price_equal_to_payment(grp))
    
def display_client(id, df):
    display(df.query('customer_unique_id == @id'))
    return None

### Managing product categories
# gathering product categories into larger categories :
main_categories = ['home', 'sports_leisure', 'electronics_and_multimedia',
                   'toys', 'auto', 'tools_and_professional_material',
                   'health_and_beauty', 'pet_shop', 'baby',
                   'watches_gifts', 'art_cinema_music', 'stationery',
                   'fashion', 'food_or_drinks',
                   'cool_stuff', 'books', 'security', 'market_place',
                   'party_supplies', 'flowers']

def map_to_larger_categories(elem):
    """ Function for mapping product categories to larger ones. """
    if elem in ['office_furniture',
                'home_comfort_2',
                'la_cuisine',
                'furniture_mattress_and_upholstery',
                'furniture_bedroom',
                'furniture_living_room',
                'fixed_telephony',
                'home_appliances',
                'small_appliances_home_oven_and_coffee',
                'home_appliances_2',
                'kitchen_dining_laundry_garden_furniture',
                'bed_bath_table',
                'furniture_decor',
                'home_confort',
                'housewares',
                'fixed_telephony']:
        return "home"
    
    elif elem in ['fashion_childrens_clothes',
                  'fashion_sport',
                  'fashion_underwear_beach',
                  'fashion_shoes',
                  'fashion_male_clothing',
                  'fashion_bags_accessories',
                  'luggage_accessories',
                  'fashio_female_clothing',]:
        return "fashion"
    
    elif elem in ['diapers_and_hygiene',
                   'baby',]:
        return "baby"
    
    elif elem in ['perfumery',
                  'health_beauty',]:
        return "health_and_beauty"
    
    elif elem in ['arts_and_craftmanship',
                  'cds_dvds_musicals',
                  'cine_photo',
                  'audio',
                  'dvds_blu_ray',
                  'music',
                  'musical_instruments',
                  'art',]:
        return "art_cinema_music"
    
    elif elem in ['books_technical',
                'books_imported',
                'books_general_interest',]:
        return "books"
    
    elif elem in ['costruction_tools_garden',
                  'agro_industry_and_commerce',
                  'construction_tools_safety',
                  'industry_commerce_and_business',
                  'construction_tools_construction',
                  'costruction_tools_tools',
                  'home_construction',
                  'construction_tools_lights',
                  'garden_tools',
                  'air_conditioning',]:
        return "tools_and_professional_material"
    
    elif elem in ['security_and_services',
                  'signaling_and_security',]:
        return "security"
    
    elif elem in ['computers',
                  'tablets_printing_image',
                  'electronics',
                  'consoles_games',
                  'telephony',
                  'computers_accessories',
                  'small_appliances',]:
        return "electronics_and_multimedia"
    
    elif elem in ['cool_stuff',
                  'party_supplies',
                  'food',
                  'drinks',
                  'food_drink',
                  'christmas_supplies',
                  'party_supplies', 
                  'market_place',
                  'flowers']:
        return "other"
    else:
        return elem

### Features engineering
def client_orders_summary(client_info):
    """ Return a df with one line per order made by the client. Works if
    the client_info is passed under the format of the merged_df 
    in the section 2."""
    return (
        client_info.groupby('order_id')
        .agg(
                order_status=('order_status', 'first'),
                order_purchase_timestamp=('order_purchase_timestamp', 'first'),
                total_order_cost=('total_order_cost', 'first'),
                cost_minus_payment=('cost_minus_payment', 'first'),
                number_of_items=('order_item_id', 'max'),
                review_score_min=('review_score', 'min'),
                review_score_mean=('review_score', 'mean'),
                review_score_max=('review_score', 'max'),
                payment_installments=('payment_installments', 'max'),
            )
    )

def relatives_to_now(orders_summary, now):
    """ Return the t-uple 
    (
        'number_of_purchases_last_365_days',
        'number_of_purchases_last_90_days',
        'number_of_purchases_last_30_days',
        'elapsed_days_since_last_purchase'
    ) 
    """
    orders_summary['now'] = now
    orders_summary['days_since_order'] = ((orders_summary.now
                                           - (orders_summary
                                              .order_purchase_timestamp))
                                          .dt.days)
    
    return (
                len(orders_summary.query("days_since_order <= 365")),
                len(orders_summary.query("days_since_order <= 90")),
                len(orders_summary.query("days_since_order <= 30")),
                orders_summary['days_since_order'].min(),
    )
    
### SECOND FEATURE ENGINEERING
def values_per_payment_type_in_an_order(order_info):
    # Create a df where rows are all the distinct payments of the
    # sequence, with 2 columns (payment type and payment value).
    payment_values_per_type_not_grouped = (
        order_info
        .groupby('payment_sequential')[['payment_type', 'payment_value']]
        .agg('first')
    )
    # Group by payment type summing.
    payment_values_per_type = (
        payment_values_per_type_not_grouped
        .groupby('payment_type')
        .sum()
        .T
        .add_prefix('payment_value_')
    )
    return payment_values_per_type

def values_per_category_and_freight_in_an_order(order_info):
    info_per_item = (
        order_info
        .groupby('order_item_id')[
            
            ['large_product_category',
             'price',
             'freight_value']
            
        ].agg('first')
    )
    
    payment_and_freight_values_per_category = (
        info_per_item
        .groupby('large_product_category')
        .sum()
        .T
        .add_prefix('value_')
    )
        
    return payment_and_freight_values_per_category



def standardized_value_per_category_and_freight_in_an_order(val_per_cat_order):
    large_product_categories = ['home',
                                'sports_leisure',
                                'electronics_and_multimedia',
                                'unknown',
                                'toys',
                                'auto',
                                'tools_and_professional_material',
                                'health_and_beauty',
                                'pet_shop',
                                'baby',
                                'watches_gifts',
                                'art_cinema_music',
                                'stationery',
                                'fashion',
                                'other',
                                'books',
                                'security',]
    
    n_cat = len(large_product_categories)
    idx_names = ['value_' + cat for cat in large_product_categories]
    idx_names.append('freight')
    
    standard_val_per_cat = pd.Series(np.zeros(len(idx_names)), idx_names)
    # Add each non-zero value
    for col_name in val_per_cat_order.columns:
        standard_val_per_cat.loc[col_name] = (val_per_cat_order
                                              .loc['price', col_name])
    # Sum all freight values in one freight class
    standard_val_per_cat.loc['freight_value'] = (val_per_cat_order
                                                 .loc['freight_value', :]
                                                 .sum())
    return standard_val_per_cat  

def standardized_value_per_payment_type_in_an_order(val_per_pay_type):
    payment_types = ['credit_card', 'debit_card', 'voucher',
                    'boleto', 'not_defined']
    
    n_type = len(payment_types)
    idx_names = ['payment_value_' + cat for cat in payment_types]
    # default to 0 for all-type a priori
    standard_val_per_pay_type = pd.Series(np.zeros(len(idx_names)), idx_names)
    
    # Add non-zero value(s)
    for col_name in val_per_pay_type.columns:
        standard_val_per_pay_type.loc[col_name] = (val_per_pay_type
                                                   .loc['payment_value',
                                                        col_name])
    return standard_val_per_pay_type  



def make_client_orders_summary(client_info):
    """ return a df with a line summary per order """
    # Empty dataframe to contain the
    orders_summary = pd.DataFrame({})
    # Build the client's orders summary, order by order.
    for order_id, order_info in client_info.groupby('order_id').__iter__():
        orders_summary[order_id] = make_unique_order_summary(order_info)
    
    return orders_summary.T




def make_unique_order_summary(order_info):
    """ return a pd.Series with information of the order """
    # Extracting values
    df = pd.Series({
        'order_status': order_info.order_status.iloc[0],
        'binary_order_status': order_info.binary_order_status.iloc[0],
        'purchase_time': order_info.order_purchase_timestamp.iloc[0],
        'delivery_time': order_info.order_delivered_customer_date.iloc[0],
        'n_items': order_info.order_item_id.max(),
        'order_cost': order_info.total_order_cost.iloc[0],
        'order_cost_minus_payment': order_info.cost_minus_payment.iloc[0],
        'review_score': order_info.review_score.mean(),
        'payment_installments': order_info.payment_installments.max()   
    })
    
    derived_df = pd.Series({
            'days_between_purchase_and_delivery': (df.delivery_time
                                                   - df.purchase_time).days,
            'hour_of_purchase': df.purchase_time.hour,
            'weekday_of_purchase': df.purchase_time.day_of_week,
    })
    
    return pd.concat(
        [
            df,
            derived_df,
            standardized_value_per_category_and_freight_in_an_order(
                values_per_category_and_freight_in_an_order(order_info)
            ),
            standardized_value_per_payment_type_in_an_order(
                values_per_payment_type_in_an_order(order_info)                                                
            ),
        ], axis=0
    )

def process_orders_summary_according_to_now(df, now):
    """ A step to prepare the client data processing """
    df.loc[:, 'now'] = now
    df.loc[:, 'elapsed_days'] = (df.now - df.purchase_time).dt.days
    return df

def map_moment_of_the_day(hour):
    if 0 <= hour < 6:
        return "night"
    elif 6 <= hour < 11:
        return "morning"
    elif 11 <= hour < 14:
        return "midday"
    elif 14 <= hour < 18:
        return "afternoon"
    else:
        return "evening"
  
def map_moment_of_the_week(day_of_week):
    if 0 <= day_of_week < 4:
        return "Monday-Thursday"
    else:
        return "Friday-Sunday"
    
    
def orders_summary_post_processing(orders_df, now):
    # To avoid warnings
    df = orders_df
    # Values relative to now
    df = process_orders_summary_according_to_now(df, now)
    # Purchasing moments into categories
    df.loc[:, 'week_moment_purchase'] = (df.hour_of_purchase
                                         .map(map_moment_of_the_week))
    df.loc[:, 'day_moment_purchase'] = (df.weekday_of_purchase
                                        .map(map_moment_of_the_day))
    # Delay_purchase_delivery
    df.loc[:, 'delay_purchase_delivery'] = (df.delivery_time
                                            - df.purchase_time).dt.days
    return df
    
    
def values_relatives_to_now_for_a_client(orders_df, now):
    """ input : orders_df_process_according_to_now """
    s = pd.Series({
        'days_last_purchase': orders_df.elapsed_days.min(),
        'days_first_purchase': orders_df.elapsed_days.max(),
    })
    
    s.loc['days_middle'] = s.days_first_purchase / 2
    
    df_first_half = orders_df.query('elapsed_days >= @s.loc["days_middle"]')
    df_second_half = orders_df.query('elapsed_days < @s.loc["days_middle"]')
    
    s.loc['number_of_purchases_first_half'] = len(df_first_half)
    s.loc['number_of_purchases_second_half'] = len(df_second_half)
    s.loc['value_spent_first_half'] = df_first_half.order_cost.sum()
    s.loc['value_spent_second_half'] = df_second_half.order_cost.sum()
    
    
    # s.loc['number_of_purchases_first_half'] = 
    return s

def find_preferred_week_moment(week_moment_purchases):
    counts = week_moment_purchases.value_counts()
    if len(counts) == 1:
        return counts.loc[0]
    elif counts.loc[0] > counts.loc[1]:
        return counts.loc[0]
    else:
        return np.NaN
    
def find_preferred_day_moment(day_moment_purchases):
    counts = day_moment_purchases.value_counts()
    if len(counts) == 1:
        return counts.loc[0]
    elif counts.loc[0] > counts.loc[1]:
        return counts.loc[0]
    else:
        return np.NaN
    
    
def client_summary(df, now):
    """ return a pandas Series giving the complete information of a client :
    
    Input must be a df of all orders already processed with the 
    'orders_summary_post_processing' function.
    
    possible improvements : 
    - percentage of delivered orders
    - is last review a disappointment
    
    """
    cols_to_sum = [
        *[col for col in df.columns if col.startswith('value_')],
        'freight_value',
        *[col for col in df.columns if col.startswith('payment_value')]
    ]
    
    s = pd.concat([
        # Series 1
        pd.Series({
            'monetary_value_sum': df.order_cost.sum(),
            'monetary_value_mean_per_order': df.order_cost.mean(),
            'total_number_of_purchases': len(df),
            'max_number_of_items_ordered': df.n_items.max(),
            'min_number_of_items_ordered': df.n_items.min(),
            'mean_number_of_items_per_order': df.n_items.mean(),
            'review_score_mean': df.review_score.mean(),
            'review_score_min': df.review_score.min(),
            'review_score_max': df.review_score.max(),
            'paid_less_than_due': (df.order_cost_minus_payment > 0).any(),
            'has_had_a_non_delivered_order': (
                (df.binary_order_status == 'not_delivered').any()
            ),
            'has_contracted_payment_installments': (
                df.payment_installments.max() > 1
            ),
            'days_delivery_min': df.delay_purchase_delivery.min(),
            'days_delivery_max': df.delay_purchase_delivery.max(),
            'days_delivery_mean': df.delay_purchase_delivery.mean(),
            'preferred_week_moment_to_purchase': np.NaN,
            'preferred_hour_moment_to_purchase': np.NaN,
            
        }), 
        # Series 2 (summing values per cat and per payment_types + freight)
        df.loc[:, cols_to_sum].sum(),
        # Series relative to now (recency and evolution in time)
        # first and second half
        values_relatives_to_now_for_a_client(df, now)
    ])
    
    if s.loc['total_number_of_purchases'] > 1:
        s.loc['preferred_week_moment_to_purchase'] = (
            find_preferred_week_moment(df.week_moment_purchase)
        )
        s.loc['preferred_day_moment_to_purchase'] = (
            find_preferred_day_moment(df.day_moment_purchase)
        )
        
    return s


def make_clients_summary_relative_to_a_date(orders_df, date):
    # TODO Select all orders previous to that date
    
    # Compute the clients' summary
    df = orders_summary_post_processing(orders_df, date)
    df.groupby('customer_unique_id').apply(client_summary(df, date))
    pass

def clients_dynamic_ratios(clients, threshold_old_clients = 90):
    """ Add ratios characterizing the client dynamic through time.
    
    1 means the client is as active as in its first period.
    
    A relatively new customer has its default values set to 1 because
    it does not make sense to track how things are evolving on a small period.
    
    The periods are define w.r.t. the first purchase time of each client.
    """
    # Default values
    clients.loc[:, 'value_ratio_p2_p1'] = 1
    clients.loc[:, 'n_purchases_ratio_p2_p1'] = 1
    
    # Finding old clients.
    old_clients_idx = (clients
                       .query('days_first_purchase > @threshold_old_clients')
                       .index)
    
    clients.loc[old_clients_idx, 'value_ratio_p2_p1'] = (
        clients.value_spent_second_half
        / clients.value_spent_first_half
    ).round(2)
    clients.loc[old_clients_idx, 'n_purchases_ratio_p2_p1'] = (
        clients.number_of_purchases_second_half 
        / clients.number_of_purchases_first_half
    ).round(2)
    return clients

def clients_preferences(clients):
    """ If a trend is detected, change the default values of :
    - 'preferred_week_moment_to_purchase',
    - 'preferred_hour_moment_to_purchase'.
    
    It is only compute for multiple-time buyers
    """
    multiple_time_buyers_idx = (clients
                                .query('total_number_of_purchases > 1')
                                .index)
    
    
    

def clients_summary_post_processing(clients, threshold_old_clients = 90):
    clients.copy()
    

### TODO : clients_summary_post_processing 
# replace NaN if possible (n_orders > 2 )
        # 'preferred_payment_type': df.,
        # 'preferred_category': df.,
    
    
    
    


