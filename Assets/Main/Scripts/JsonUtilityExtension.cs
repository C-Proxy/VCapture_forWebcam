using System;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// JsonUtilityExtension.cs

/// <summary>
/// JSON ⇔ オブジェクト間の変換へのショートカットを提供します。
/// </summary>
public static class JsonUtilityExtension
{
    /// <summary>
    /// <see cref="string"/> を JSON 形式の文字列と仮定し {T} 型への変換を試行します。
    /// </summary>
    /// <remarks>
    /// 内部実装に <see cref="JsonUtility.ToJson(object)"/> を使用しているので
    /// 変換可能な規則は Unity の <see cref="UnityEngine.JsonUtility"/> に準拠します。
    /// </remarks>
    public static T FromJson<T>(this string self) => JsonUtility.FromJson<T>(self);

    /// <summary>
    /// <see cref="string"/> を Root 要素を持たない JSON 配列形式の文字列と仮定し T[] 型への変換を試行します。
    /// </summary>
    public static T[] FromJsonArray<T>(this string self) => JsonHelper.FromJson<T>(self);

    /// <summary>
    /// 指定したオブジェクトを JSON 文字列に変換します。
    /// </summary>
    /// <remarks>
    /// 内部実装に <see cref="JsonUtility.ToJson(object)"/> を使用しているので
    /// 変換可能な規則は Unity の <see cref="UnityEngine.JsonUtility"/> に準拠します。
    /// </remarks>
    public static string FromJson<T>(this object self) => JsonUtility.ToJson(self);

    /// <summary>
    /// 指定したオブジェクトを Root 要素を持たない JSON 配列に変換します。
    /// </summary>
    public static string FromJsonArray<T>(this IEnumerable<T> self) => JsonHelper.ToJson(self);
}
/// <summary>
/// <see cref="JsonUtility"/> に不足している機能を提供します。
/// </summary>
public static class JsonHelper
{
    /// <summary>
    /// 指定した string を Root オブジェクトを持たない JSON 配列と仮定してデシリアライズします。
    /// </summary>
    public static T[] FromJson<T>(string json)
    {
        // ルート要素があれば変換できるので
        // 入力されたJSONに対して(★)の行を追加する
        //
        // e.g.
        // ★ {
        // ★     "array":
        //        [
        //            ...
        //        ]
        // ★ }
        //
        string dummy_json = $"{{\"{DummyNode<T>.ROOT_NAME}\": {json}}}";
        Debug.Log(dummy_json);

        // ダミーのルートにデシリアライズしてから中身の配列を返す
        var obj = JsonUtility.FromJson<DummyNode<T>>(dummy_json);
        return obj.array;
    }

    /// <summary>
    /// 指定した配列やリストなどのコレクションを Root オブジェクトを持たない JSON 配列に変換します。
    /// </summary>
    /// <remarks>
    /// 'prettyPrint' には非対応。整形したかったら別途変換して。
    /// </remarks>
    public static string ToJson<T>(IEnumerable<T> collection)
    {
        string json = JsonUtility.ToJson(new DummyNode<T>(collection)); // ダミールートごとシリアル化する
        int start = DummyNode<T>.ROOT_NAME.Length + 4;
        int len = json.Length - start - 1;
        return json.Substring(start, len); // 追加ルートの文字を取り除いて返す
    }

    // 内部で使用するダミーのルート要素
    [Serializable]
    private struct DummyNode<T>
    {
        // 補足:
        // 処理中に一時使用する非公開クラスのため多少設計が変でも気にしない

        // JSONに付与するダミールートの名称
        public const string ROOT_NAME = nameof(array);
        // 疑似的な子要素
        public T[] array;
        // コレクション要素を指定してオブジェクトを作成する
        public DummyNode(IEnumerable<T> collection) => this.array = collection.ToArray();
    }
}